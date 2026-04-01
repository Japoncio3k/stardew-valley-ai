
from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    keywords: list[str] = Field(
        description="Uma lista de até 5 palavras chave que uma pessoa buscaria nesse texto."
    )
    summary: str = Field(
        description="Um resumo conciso de no máximo 2 frases do trecho."
    )
    hypothetical_questions: list[str] = Field(
        description="Uma lista de 2-4 perguntas com as respostas retiradas do texto. Inclua apenas perguntas que podem ser respondidas com informações do trecho. Inclua as respostas no formato 'Pergunta: ... Resposta: ...'.",  # noqa: E501
    )
    table_summary: str | None = Field(
        description="Se o trecho for uma tabela, um resumo em linguagem natural de seus principais insights.",
        default=None,
    )
