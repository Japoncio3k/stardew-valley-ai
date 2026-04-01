
from pydantic import BaseModel


class EnrichedChunk(BaseModel):
    is_table: bool
    content: str
    source: str
    keywords: list[str]
    summary: str
    hypothetical_questions: list[str]
    table_summary: str | None = None
