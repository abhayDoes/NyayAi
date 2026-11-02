"""SQLAlchemy engine, session factory, and declarative model base."""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    """Base class inherited by database models."""


def _make_engine():
    url = get_settings().database_url
    options = {"check_same_thread": False} if url.startswith("sqlite") else {}
    return create_engine(url, connect_args=options, future=True)


engine = _make_engine()
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def get_db():
    """Yield a database session and always close it after the request."""
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
