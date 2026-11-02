"""Import model classes here so SQLAlchemy can register their tables."""

from app.models.judgment import Judgment
from app.models.research import Research

__all__ = ["Judgment", "Research"]
