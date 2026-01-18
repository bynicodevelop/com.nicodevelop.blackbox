"""Test fixtures for scoring module tests."""

from datetime import date, time

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from blackbox.core.scoring.config import ScoringConfig
from blackbox.data.models import EconomicEvent, EventType, Impact
from blackbox.data.storage.models import Base
from blackbox.data.storage.repository import EventRepository


@pytest.fixture
def scoring_config() -> ScoringConfig:
    """Default scoring configuration for tests."""
    return ScoringConfig(
        half_life_hours=48.0,
        lookback_days=7,
        min_bias_threshold=1.0,
    )


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
def event_repository(test_session) -> EventRepository:
    """Create an event repository with the test session."""
    return EventRepository(test_session)


@pytest.fixture
def sample_events() -> list[EconomicEvent]:
    """Sample events for scoring tests.

    Creates events for USD and EUR with various surprises and weights.
    """
    return [
        # USD events - positive surprises
        EconomicEvent(
            date=date(2026, 1, 15),
            time=time(8, 30),
            currency="USD",
            impact=Impact.HIGH,
            event_name="Non-Farm Employment Change",
            actual=250.0,
            forecast=200.0,
            previous=180.0,
            event_type=EventType.EMPLOYMENT,
            direction=1,
            weight=8,
        ),
        EconomicEvent(
            date=date(2026, 1, 14),
            time=time(10, 0),
            currency="USD",
            impact=Impact.MEDIUM,
            event_name="CPI",
            actual=3.5,
            forecast=3.2,
            previous=3.0,
            event_type=EventType.INFLATION,
            direction=-1,  # Higher inflation is bearish
            weight=6,
        ),
        # EUR events - mixed surprises
        EconomicEvent(
            date=date(2026, 1, 15),
            time=time(9, 0),
            currency="EUR",
            impact=Impact.HIGH,
            event_name="ECB Rate Decision",
            actual=4.5,
            forecast=4.25,
            previous=4.0,
            event_type=EventType.INTEREST_RATE,
            direction=1,
            weight=10,
        ),
        EconomicEvent(
            date=date(2026, 1, 13),
            time=time(11, 0),
            currency="EUR",
            impact=Impact.MEDIUM,
            event_name="German PMI",
            actual=48.0,
            forecast=51.0,
            previous=50.0,
            event_type=EventType.PMI,
            direction=1,
            weight=5,
        ),
        # Event without surprise (no actual yet)
        EconomicEvent(
            date=date(2026, 1, 16),
            time=time(14, 0),
            currency="USD",
            impact=Impact.HIGH,
            event_name="Retail Sales",
            actual=None,
            forecast=0.5,
            previous=0.3,
            event_type=EventType.GROWTH,
            direction=1,
            weight=7,
        ),
    ]


@pytest.fixture
def sample_events_bullish_eur() -> list[EconomicEvent]:
    """Events that create a bullish EUR/USD signal (EUR score > USD score)."""
    return [
        EconomicEvent(
            date=date(2026, 1, 15),
            time=time(9, 0),
            currency="EUR",
            impact=Impact.HIGH,
            event_name="ECB Rate Hike",
            actual=5.0,
            forecast=4.5,
            previous=4.0,
            event_type=EventType.INTEREST_RATE,
            direction=1,
            weight=10,
        ),
        EconomicEvent(
            date=date(2026, 1, 15),
            time=time(8, 30),
            currency="USD",
            impact=Impact.HIGH,
            event_name="Weak NFP",
            actual=100.0,
            forecast=200.0,
            previous=180.0,
            event_type=EventType.EMPLOYMENT,
            direction=1,
            weight=8,
        ),
    ]


@pytest.fixture
def sample_events_bearish_eur() -> list[EconomicEvent]:
    """Events that create a bearish EUR/USD signal (USD score > EUR score)."""
    return [
        EconomicEvent(
            date=date(2026, 1, 15),
            time=time(9, 0),
            currency="EUR",
            impact=Impact.HIGH,
            event_name="ECB Disappoints",
            actual=4.0,
            forecast=4.5,
            previous=4.5,
            event_type=EventType.INTEREST_RATE,
            direction=1,
            weight=10,
        ),
        EconomicEvent(
            date=date(2026, 1, 15),
            time=time(8, 30),
            currency="USD",
            impact=Impact.HIGH,
            event_name="Strong NFP",
            actual=300.0,
            forecast=200.0,
            previous=180.0,
            event_type=EventType.EMPLOYMENT,
            direction=1,
            weight=8,
        ),
    ]
