"""Schemas for editable retrieval inputs and source-grounded results."""

from pydantic import BaseModel, ConfigDict, Field


class RetrievalRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    facts: list[str] = Field(min_length=1, max_length=12)
    legal_issues: list[str] = Field(min_length=1, max_length=10)
    search_queries: list[str] = Field(min_length=1, max_length=5)
    court: str | None = None
    fromdate: str | None = None
    todate: str | None = None
    max_judgments: int = Field(default=5, ge=1, le=5)
    passages_per_judgment: int = Field(default=3, ge=1, le=5)


class RetrievedPassage(BaseModel):
    text: str
    keyword_score: float = Field(ge=0, le=1)
    matched_terms: list[str] = Field(default_factory=list)


class RetrievedJudgment(BaseModel):
    document_id: str
    case_name: str
    court: str | None = None
    judgment_date: str | None = None
    case_number: str | None = None
    source_url: str
    keyword_score: float = Field(ge=0, le=1)
    matched_terms: list[str] = Field(default_factory=list)
    passages: list[RetrievedPassage] = Field(default_factory=list)


class RetrievalResponse(BaseModel):
    method: str = "keyword_overlap"
    searched_queries: list[str]
    judgments: list[RetrievedJudgment]
    warnings: list[str] = Field(default_factory=list)
