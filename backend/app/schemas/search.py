"""Validated search and document response schemas."""

from pydantic import BaseModel, Field


class JudgmentSearchResult(BaseModel):
    document_id: str
    case_name: str
    court: str | None = None
    judgment_date: str | None = None
    case_number: str | None = None
    snippet: str | None = None
    source_url: str
    document_size: int | None = None


class JudgmentSearchResponse(BaseModel):
    query: str
    page: int
    found: str | None = None
    results: list[JudgmentSearchResult] = Field(default_factory=list)


class JudgmentDocumentResponse(JudgmentSearchResult):
    full_text: str
