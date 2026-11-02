"""Request schema for a lawyer's case description."""

from pydantic import BaseModel, ConfigDict, Field


class CaseAnalysisRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    description: str = Field(min_length=20, max_length=20_000)
