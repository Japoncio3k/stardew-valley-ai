import re
import time
from datetime import datetime
from typing import Any

from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableSerializable
from unstructured.documents.elements import Element as UnstructuredElement

from data_ingestion.models.chunk_metadata import ChunkMetadata
from data_ingestion.models.strings_to_ignore import strings_to_ignore
from data_ingestion.utils.open_router_manager import OpenRouterManager
from data_ingestion.utils.print_with_timestamp import print_with_timestamp


def generate_enrichment_prompt(chunk_text: str, is_table: bool) -> str:
    """Generates a prompt for the LLM to enrich a chunk."""
    chunk_text = re.sub(r"{", "{{", chunk_text)
    chunk_text = re.sub(r"}", "}}", chunk_text)
    table_instruction = (
        """
    Esse chunk é uma TABELA. Seu resumo deve descrever os principais pontos de dados e tendências,
    por exemplo: 'Esta tabela mostra que a fruta X é mais lucrativa na estação Y.'
    """
        if is_table
        else "Esse chunk é um texto comum. Deixe o campo table_summary vazio."
    )

    prompt = f"""
    Você é um especialista no jogo Stardew Valley. Analise o seguinte trecho de um documento
    relacionado ao jogo e gere os metadados especificados:
    {table_instruction}
    Chunk Content:
    ---
    {chunk_text}
    ---
    Requisitos de Metadados:
    hypothetical_questions: Crie uma lista de 2-4 perguntas que poderiam ser feitas sobre o
    conteúdo do trecho. Inclua apenas perguntas que podem ser respondidas com informações do
    trecho. SEMPRE inclua as respostas retiradas do trecho no formato Pergunta:...; Resposta:....
    Não mencione o trecho nas perguntas.
    """
    return prompt


def create_chain(chunk: UnstructuredElement) -> RunnableSerializable[Any, Any]:
    is_table = "text_as_html" in chunk.metadata.to_dict()
    content = chunk.metadata.text_as_html if is_table else chunk.text

    assert content is not None
    prompt = generate_enrichment_prompt(content, is_table)
    chain = ChatPromptTemplate.from_template(
        prompt
    ) | OpenRouterManager().llm.with_structured_output(schema=ChunkMetadata)
    return chain


def enrich_chunk(chunk: UnstructuredElement, iterations: int = 0) -> ChunkMetadata:
    """Enriches a single chunk with LLM-generated metadata."""
    is_table = "text_as_html" in chunk.metadata.to_dict()
    content = chunk.metadata.text_as_html if is_table else chunk.text

    assert content is not None

    prompt = generate_enrichment_prompt(content, is_table)

    try:
        current_time = time.time()
        metadata_obj: ChunkMetadata = OpenRouterManager().llm.invoke(prompt)  # type:ignore
        date = datetime.now().strftime("%H:%M:%S")
        print(
            f"[{date}] Generated Metadata in {time.time() - current_time:.2f} seconds."
        )
        return metadata_obj
    except Exception as e:
        print(f"  - Error enriching chunk: {e}")
        if "Error code: 429" in str(e):
            OpenRouterManager().set_next_key()
        if iterations < 5:
            return enrich_chunk(chunk, iterations + 1)
        raise e


def enrich_page_chunks(
    chunks: list[UnstructuredElement], url: str
) -> list[dict[str, Any]]:
    """Enriches a list of chunks with LLM-generated metadata."""
    enriched_chunks = []

    if url == "/stardew_valley_wiki":
        return [
            {
                "content": chunk.metadata.text_as_html
                if "text_as_html" in chunk.metadata.to_dict()
                else chunk.text,
                "source": url,
            }
            for chunk in chunks
        ]
    chains = {}
    inputs = {}
    chunks_to_enrich: list[UnstructuredElement] = []

    for chunk in chunks:
        is_table = "text_as_html" in chunk.metadata.to_dict()
        if is_table and chunk.metadata.text_as_html in strings_to_ignore:
            continue
        chunks_to_enrich.append(chunk)

    for index2, chunk in enumerate(chunks_to_enrich):
        print_with_timestamp(
            f"Generating chain for chunk {index2 + 1}/{len(chunks_to_enrich)}..."
        )

        chains[str(index2)] = create_chain(chunk)
        inputs[str(index2)] = "."

    print_with_timestamp(f"Running {len(chunks)} enrichment chains in parallel...")
    current_time = time.time()
    runnable = RunnableParallel(chains).with_retry(
        stop_after_attempt=3, retry_if_exception_type=(ValueError,)
    )

    results = runnable.invoke(inputs)

    print_with_timestamp(
        f"Completed enrichment of all chunks in {time.time() - current_time:.2f} seconds.."
    )

    for index2, chunk in enumerate(chunks_to_enrich):
        is_table = "text_as_html" in chunk.metadata.to_dict()
        enriched_metadata: ChunkMetadata = results[str(index2)]
        enriched_chunks.append(
            {
                "is_table": is_table,
                "content": chunk.metadata.text_as_html if is_table else chunk.text,
                "source": url,
                "keywords": enriched_metadata.keywords,
                "summary": enriched_metadata.summary,
                "hypothetical_questions": enriched_metadata.hypothetical_questions,
                "table_summary": enriched_metadata.table_summary,
            }
        )

    return enriched_chunks
