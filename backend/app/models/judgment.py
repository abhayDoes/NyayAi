"""A judgment record linked to its original Indian Kanoon document ID."""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Judgment(Base):
    __tablename__ = "judgments"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    document_id: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    research_id: Mapped[int | None] = mapped_column(ForeignKey("research.id"), nullable=True)
    case_name: Mapped[str | None] = mapped_column(String(500), nullable=True)
    court: Mapped[str | None] = mapped_column(String(200), nullable=True)
    judgment_date: Mapped[str | None] = mapped_column(String(40), nullable=True)
    case_number: Mapped[str | None] = mapped_column(String(200), nullable=True)
    source_url: Mapped[str] = mapped_column(String(1000))
    snippet: Mapped[str | None] = mapped_column(Text, nullable=True)
    full_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
