"""Validated input and output for case description analysis."""

from pydantic import BaseModel, ConfigDict, Field


class CaseAnalysis(BaseModel):
    model_config = ConfigDict(extra="forbid")

    case_category: str = Field(min_length=1, max_length=120)
    facts: list[str] = Field(min_length=1, max_length=12)
    legal_issues: list[str] = Field(min_length=1, max_length=10)
    legal_terminology: list[str] = Field(max_length=20)
    search_queries: list[str] = Field(min_length=1, max_length=8)
