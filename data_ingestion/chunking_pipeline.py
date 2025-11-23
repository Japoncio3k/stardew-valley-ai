import json
import os
import re
import time
from typing import Any, List
from urllib.parse import unquote
from xml.dom.minidom import Element, Node, parseString

import requests
from langchain_core.prompts.chat import ChatPromptTemplate
from langchain_core.runnables import RunnableParallel, RunnableSerializable
from pydantic import BaseModel, ConfigDict
from strings_to_ignore import strings_to_ignore
from unstructured.chunking.title import chunk_by_title
from unstructured.documents.elements import Element as UnstructuredElement
from unstructured.partition.html import partition_html

from models.chunk_metadata import ChunkMetadata
from utils import print_with_timestamp
from utils.open_router_manager import OpenRouterManager

default_url = "https://pt.stardewvalleywiki.com"
default_path = "output"


class PageData(BaseModel):
    model_config = ConfigDict(arbitrary_types_allowed=True)
    urls: list[str]
    chunks: list[UnstructuredElement]


def save_progress(checked_urls: list[str], urls: list[str]) -> None:
    """Saves the current progress to a JSON file."""
    with open("data.json", "w+", encoding="utf-8") as fp:
        progress = {
            "checked_urls": checked_urls,
            "urls": urls,
        }
        fp.write(json.dumps(progress, ensure_ascii=False, indent=4))


def treat_html(html: str) -> str:
    """Treats HTML content to make it parseable."""
    html = re.sub(r"<script.*?>.*?</script>", "", html, flags=re.DOTALL)
    html = re.sub(r"<style.*?>.*?</style>", "", html, flags=re.DOTALL)
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)
    html = re.sub(r"\s+", " ", html)
    html = re.sub(r"> <", ">\n<", html)
    html = re.sub(r"><", ">\n<", html)
    html = re.sub(r'<input(.*?)">', '<input\\1"/>', html)
    html = re.sub(r"<input(.*?) >", "<input\\1 />", html)
    html = re.sub(r"<img([^>]+) >", "<img\\1 />", html)
    html = re.sub(r'<img([^>]+)">', '<img\\1"/>', html)
    html = re.sub(r"&lrm;", "", html)
    html = re.sub(r"&gt;", ">", html)
    html = re.sub(r'>data-sort-value="(\d+)">', ">\\1 ouros", html)
    html = re.sub(r'>data-sort-value="(\d\s+)";', ">\\1 ouros", html)
    html = re.sub(r"<link(.*?)>", "", html)
    html = re.sub(r"<br>", "", html)
    return html


def compareable_url_list(urls: list[str]) -> list[str]:
    new_list = []
    for url in urls:
        new_list.append(treat_url(url).lower().replace(".json", "").removeprefix("/"))
    return new_list


def compareable_url(url: str) -> str:
    return treat_url(url).lower().replace(".json", "").removeprefix("/")


def treat_url(url: str) -> str:
    return unquote(url)


def should_visit(url: str) -> bool:
    """Determines if a URL should be visited."""
    lower_url = url.lower()
    return (
        url.startswith("/")
        and "mediawiki" not in lower_url
        and "ficheiro:" not in lower_url
        and "#" not in lower_url
        and "utilizador_discussão" not in lower_url
        and "histórico_de_versões" not in lower_url
        and "utilizadora_discussão" not in lower_url
        and "utilizadora" not in lower_url
        and "modificações" not in lower_url
        and "pesquisar/" not in lower_url
        and "mobilelanguages" not in lower_url
        and "especial:history" not in lower_url
    )


def get_urls(content: Element) -> list[str]:
    """Gets all URLs from a page's content."""
    urls: list[str] = []
    if content.childNodes:
        for node in content.childNodes:
            if node.nodeType == Node.ELEMENT_NODE and node.tagName == "a":
                href = treat_url(node.getAttribute("href"))
                if href and should_visit(href):
                    urls.append(href)
            urls.extend(get_urls(node))

    return urls


def get_content_from_page(html: str) -> Element:
    """Gets the main content from a page's HTML."""
    html = treat_html(html)

    try:
        html_parsed = parseString(html)

    except Exception as e:
        print_with_timestamp("Error parsing HTML:", e)
        print_with_timestamp(html)
        raise e
    body = html_parsed.childNodes[1].childNodes[3]
    if len(body.childNodes) > 5:
        content = (
            html_parsed.childNodes[1]
            .childNodes[3]
            .childNodes[5]
            .childNodes[9]
            .childNodes[13]
            .childNodes[1]
        )
    else:
        content = html_parsed.childNodes[1].childNodes[3].childNodes[1]

    return content


def get_data_from_url(url: str) -> PageData:
    """Gets data from a given URL."""
    html = requests.get(f"{default_url}{url}").text

    content = get_content_from_page(html)

    elements_for_chunking = partition_html(text=content.toxml())

    return PageData(
        urls=get_urls(content),
        chunks=chunk_by_title(elements_for_chunking, max_characters=800, overlap=100),
    )


def generate_enrichment_prompt(chunk_text: str, is_table: bool) -> str:
    """Generates a prompt for the LLM to enrich a chunk."""
    chunk_text = re.sub(r"{", "{{", chunk_text)
    chunk_text = re.sub(r"}", "}}", chunk_text)
    table_instruction = (
        """
    Esse chunk é uma TABELA. Seu resumo deve descrever os principais pontos de dados e tendências, por exemplo: 'Esta tabela mostra que a fruta X é mais lucrativa na estação Y.'
    """
        if is_table
        else "Esse chunk é um texto comum. Deixe o campo table_summary vazio."
    )

    prompt = f"""
    Você é um especialista no jogo Stardew Valley. Analise o seguinte trecho de um documento relacionado ao jogo e gere os metadados especificados:
    {table_instruction}
    Chunk Content:
    ---
    {chunk_text}
    ---
    Requisitos de Metadados:
    hypothetical_questions: Crie uma lista de 2-4 perguntas que poderiam ser feitas sobre o conteúdo do trecho. Inclua apenas perguntas que podem ser respondidas com informações do trecho. SEMPRE inclua as respostas retiradas do trecho no formato Pergunta:...; Resposta:.... Não mencione o trecho nas perguntas.
    """
    return prompt


def create_chain(chunk: UnstructuredElement) -> RunnableSerializable:
    is_table = "text_as_html" in chunk.metadata.to_dict()
    content = chunk.metadata.text_as_html if is_table else chunk.text

    assert content is not None
    prompt = generate_enrichment_prompt(content, is_table)
    chain = ChatPromptTemplate.from_template(
        prompt
    ) | OpenRouterManager().llm.with_structured_output(schema=ChunkMetadata)
    return chain


def enrich_page_chunks(
    chunks: List[UnstructuredElement], url: str
) -> list[dict[str, Any]]:
    """Enriches a list of chunks with LLM-generated metadata."""
    enriched_chunks = []

    if url == treat_url("/Stardew_Valley_Wiki"):
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


def main():
    if os.path.exists("data.json"):
        with open("data.json", "r") as fp:
            progress = json.load(fp)
            urls = progress["urls"]
            checked_urls: list[str] = progress["checked_urls"]  # type:ignore

    else:
        urls = [treat_url("/Stardew_Valley_Wiki")]

    if os.path.exists(default_path):
        used_urls = [treat_url(url) for url in os.listdir(default_path)]

    else:
        used_urls = []

    for index, url in enumerate(urls):
        try:
            print_with_timestamp(
                f"Processing URL {index + 1}/{len(urls)}: {url} [Access in {default_url}{url}]"
            )

            if compareable_url(url) in compareable_url_list(used_urls):
                print("URL already processed, skipping...")
                continue

            # Timeout used to avoid getting rate limited by the server. (between 0.5 and 1.5 seconds). Not needed if using free LLM because of latency.
            # timeout = randint(50, 150) / 100
            # print(f"Sleeping for {timeout} seconds...")
            # time.sleep(timeout)

            try:
                page_data = get_data_from_url(url)
                checked_urls.append(url)
            except Exception as e:
                save_progress(checked_urls, urls)
                raise e

            for new_url in page_data.urls:
                if compareable_url(new_url) not in compareable_url_list(urls):
                    urls.append(new_url)

            print("URL not processed yet, enriching chunks...")
            try:
                enriched_chunks = enrich_page_chunks(page_data.chunks, url)

                with open(f"output{url}.json", "w", encoding="utf-8") as fp:
                    fp.write(
                        json.dumps(
                            {"items": enriched_chunks},
                            ensure_ascii=False,
                            indent=4,
                        ),
                    )
            except Exception as e:
                save_progress(checked_urls, urls)
                raise e

            used_urls.append(url)
            print()

        except KeyboardInterrupt:
            print("Process interrupted by user. Saving progress...")
            save_progress(checked_urls, urls)
            break


if __name__ == "__main__":
    main()
