from typing import List, Optional

from pydantic import BaseModel, Field


class ChunkMetadata(BaseModel):
    keywords: List[str] = Field(
        description="Uma lista de até 5 palavras chave que uma pessoa buscaria nesse texto."
    )
    summary: str = Field(
        description="Um resumo conciso de no máximo 2 frases do trecho."
    )
    hypothetical_questions: List[str] = Field(
        description="Uma lista de 2-4 perguntas com as respostas retiradas do texto. Inclua apenas perguntas que podem ser respondidas com informações do trecho. Inclua as respostas no formato 'Pergunta: ... Resposta: ...'.",
    )
    table_summary: Optional[str] = Field(
        description="Se o trecho for uma tabela, um resumo em linguagem natural de seus principais insights.",
        default=None,
    )
