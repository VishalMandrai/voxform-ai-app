"""
Database engine and session management.

This is the ONLY file in the project that knows how to construct a
SQLAlchemy engine. Repositories receive a `Session` through dependency
injection (see `get_db`) — they never import this module's engine
directly. That indirection is what lets Phase 2/3 swap MySQL for
something else, or point different modules at different databases,
without rewriting repository code.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import get_settings

settings = get_settings()

engine = create_engine(
    settings.database_url,
    pool_pre_ping=True,
    echo=settings.debug,
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


class Base(DeclarativeBase):
    """Shared declarative base — every ORM model in every module inherits this."""

    pass


def get_db() -> Generator[Session, None, None]:
    """
    FastAPI dependency that yields a request-scoped DB session.

    Routers depend on this (or on services that depend on it), never on
    `SessionLocal` directly — keeps session lifecycle in one place.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
