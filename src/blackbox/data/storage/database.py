"""Database connection and session management.

This module provides utilities for connecting to PostgreSQL
and managing database sessions.
"""

import os
from collections.abc import Generator
from contextlib import contextmanager

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from blackbox.data.storage.models import Base

# Default database URL (can be overridden via environment variable)
DEFAULT_DATABASE_URL = (
    "postgresql+psycopg2://blackbox:blackbox_dev@localhost:5432/blackbox"
)

_engine: Engine | None = None
_SessionLocal: sessionmaker | None = None


def get_database_url() -> str:
    """Get the database URL from environment or use default.

    Returns:
        The database connection URL.
    """
    return os.environ.get("DATABASE_URL_SYNC", DEFAULT_DATABASE_URL)


def get_engine(url: str | None = None) -> Engine:
    """Get or create the SQLAlchemy engine.

    Args:
        url: Optional database URL. If not provided, uses environment variable
             or default.

    Returns:
        SQLAlchemy Engine instance.
    """
    global _engine
    if _engine is None:
        database_url = url or get_database_url()
        _engine = create_engine(
            database_url,
            pool_pre_ping=True,
            pool_size=5,
            max_overflow=10,
        )
    return _engine


def get_session_factory(engine: Engine | None = None) -> sessionmaker:
    """Get or create the session factory.

    Args:
        engine: Optional SQLAlchemy engine. If not provided, uses default.

    Returns:
        SQLAlchemy sessionmaker instance.
    """
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=engine or get_engine(),
            autocommit=False,
            autoflush=False,
        )
    return _SessionLocal


@contextmanager
def get_session(engine: Engine | None = None) -> Generator[Session, None, None]:
    """Context manager for database sessions.

    Provides a transactional scope around a series of operations.
    Commits on success, rolls back on exception.

    Args:
        engine: Optional SQLAlchemy engine.

    Yields:
        SQLAlchemy Session instance.

    Example:
        with get_session() as session:
            repo = EventRepository(session)
            events = repo.get_events(start_date, end_date)
    """
    session_factory = get_session_factory(engine)
    session = session_factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def init_db(engine: Engine | None = None) -> None:
    """Initialize the database by creating all tables.

    Args:
        engine: Optional SQLAlchemy engine. If not provided, uses default.
    """
    engine = engine or get_engine()
    Base.metadata.create_all(bind=engine)


def reset_engine() -> None:
    """Reset the global engine and session factory.

    Useful for testing or when changing database connections.
    """
    global _engine, _SessionLocal
    if _engine is not None:
        _engine.dispose()
    _engine = None
    _SessionLocal = None
