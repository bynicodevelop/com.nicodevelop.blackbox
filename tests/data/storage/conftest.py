"""Test fixtures for storage module tests."""

from datetime import date, time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from blackbox.data.models import EconomicEvent, Impact
from blackbox.data.storage.models import Base


@pytest.fixture
def test_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def test_session(test_engine):
    """Create a database session for testing."""
    SessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)
    session = SessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture
def sample_events_for_db() -> list[EconomicEvent]:
    """Create sample events for database testing."""
    return [
        EconomicEvent(
            date=date(2026, 1, 15),
            time=time(8, 30),
            currency="USD",
            impact=Impact.HIGH,
            event_name="Non-Farm Employment Change",
            actual="223K",
            forecast="215K",
            previous="212K",
        ),
        EconomicEvent(
            date=date(2026, 1, 15),
            time=time(10, 0),
            currency="EUR",
            impact=Impact.MEDIUM,
            event_name="ECB President Speech",
            actual=None,
            forecast=None,
            previous=None,
        ),
        EconomicEvent(
            date=date(2026, 1, 16),
            time=time(14, 0),
            currency="USD",
            impact=Impact.LOW,
            event_name="Treasury Budget Statement",
            actual="-50B",
            forecast="-45B",
            previous="-40B",
        ),
        EconomicEvent(
            date=date(2026, 1, 17),
            time=None,
            currency="JPY",
            impact=Impact.HOLIDAY,
            event_name="Bank Holiday",
            actual=None,
            forecast=None,
            previous=None,
        ),
    ]


@pytest.fixture
def future_events_for_db() -> list[EconomicEvent]:
    """Create future events without actual values for testing updates."""
    return [
        EconomicEvent(
            date=date(2026, 2, 15),
            time=time(8, 30),
            currency="USD",
            impact=Impact.HIGH,
            event_name="CPI Release",
            actual=None,
            forecast="3.2%",
            previous="3.1%",
        ),
        EconomicEvent(
            date=date(2026, 2, 16),
            time=time(10, 0),
            currency="GBP",
            impact=Impact.HIGH,
            event_name="Bank Rate Decision",
            actual=None,
            forecast="5.25%",
            previous="5.25%",
        ),
    ]
