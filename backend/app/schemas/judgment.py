"""Public response shape for judgment metadata."""

from pydantic import BaseModel, ConfigDict


class JudgmentSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    document_id: str
    case_name: str | None = None
    court: str | None = None
    judgment_date: str | None = None
    case_number: str | None = None
    source_url: str
    snippet: str | None = None
