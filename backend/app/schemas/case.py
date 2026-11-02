"""Schemas for a lawyer's case description."""

from pydantic import BaseModel, Field


class CaseDescription(BaseModel):
    description: str = Field(min_length=20, max_length=20_000)
