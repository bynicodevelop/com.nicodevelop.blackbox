"""Tests for the CalendarService class."""

from datetime import date, time
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from blackbox.data.models import EconomicEvent, Impact
from blackbox.data.services import CalendarService
from blackbox.data.storage.models import Base


@pytest.fixture
def test_engine():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(bind=engine)
    yield engine
    engine.dispose()


@pytest.fixture
def mock_get_session(test_engine):
    """Mock the get_session function to use test database."""
    SessionLocal = sessionmaker(bind=test_engine, autocommit=False, autoflush=False)

    from contextlib import contextmanager

    @contextmanager
    def get_session_mock():
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    with patch("blackbox.data.services.get_session", get_session_mock):
        yield


@pytest.fixture
def sample_events_by_date():
    """Create sample events indexed by date for scraper mock."""
    return {
        date(2026, 1, 15): [
            EconomicEvent(
                date=date(2026, 1, 15),
                time=time(8, 30),
                currency="USD",
                impact=Impact.HIGH,
                event_name="NFP",
                actual="200K",
                forecast="195K",
                previous="190K",
            ),
        ],
        date(2026, 1, 16): [
            EconomicEvent(
                date=date(2026, 1, 16),
                time=time(10, 0),
                currency="EUR",
                impact=Impact.MEDIUM,
                event_name="CPI",
                actual=None,
                forecast="2.5%",
                previous="2.4%",
            ),
        ],
    }


def create_mock_scraper(events_by_date: dict):
    """Helper to create a mock scraper that returns events by date."""
    mock_scraper = MagicMock()

    def fetch_day_side_effect(target_date):
        return events_by_date.get(target_date, [])

    mock_scraper.fetch_day.side_effect = fetch_day_side_effect
    mock_scraper.browser = MagicMock()
    mock_scraper.browser.pagination_delay = MagicMock()
    mock_scraper.__enter__ = MagicMock(return_value=mock_scraper)
    mock_scraper.__exit__ = MagicMock(return_value=False)
    return mock_scraper


class TestCalendarServiceFetchMonth:
    """Tests for the fetch_month method."""

    def test_fetch_month_scrapes_day_by_day(
        self, mock_get_session, sample_events_by_date
    ):
        """Test that fetch_month scrapes each day and persists immediately."""
        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            mock_scraper = create_mock_scraper(sample_events_by_date)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()
            events = service.fetch_month(2026, 1)

            # Verify fetch_day was called for each day of January (31 days)
            assert mock_scraper.fetch_day.call_count == 31
            # Should have 2 events total (from days 15 and 16)
            assert len(events) == 2

    def test_fetch_month_skips_existing_days(
        self, mock_get_session, sample_events_by_date
    ):
        """Test that fetch_month skips days that already have data."""
        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            mock_scraper = create_mock_scraper(sample_events_by_date)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()

            # First call - should scrape all 31 days
            service.fetch_month(2026, 1)
            first_call_count = mock_scraper.fetch_day.call_count
            assert first_call_count == 31

            # Second call - should skip days with existing data
            mock_scraper.fetch_day.reset_mock()
            events = service.fetch_month(2026, 1)

            # Should skip days 15 and 16 (have data), scrape remaining 29 days
            assert mock_scraper.fetch_day.call_count == 29
            assert len(events) == 2

    def test_fetch_month_force_refresh_scrapes_all(
        self, mock_get_session, sample_events_by_date
    ):
        """Test that force_refresh scrapes all days regardless of cache."""
        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            mock_scraper = create_mock_scraper(sample_events_by_date)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()

            # First call - scrape all
            service.fetch_month(2026, 1)
            assert mock_scraper.fetch_day.call_count == 31

            # Second call with force_refresh - should scrape all again
            mock_scraper.fetch_day.reset_mock()
            service.fetch_month(2026, 1, force_refresh=True)
            assert mock_scraper.fetch_day.call_count == 31

    def test_fetch_month_applies_currency_filter(
        self, mock_get_session, sample_events_by_date
    ):
        """Test that currency filter is applied correctly."""
        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            mock_scraper = create_mock_scraper(sample_events_by_date)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()
            events = service.fetch_month(2026, 1, currencies=["USD"])

            assert len(events) == 1
            assert events[0].currency == "USD"

    def test_fetch_month_applies_impact_filter(
        self, mock_get_session, sample_events_by_date
    ):
        """Test that impact filter is applied correctly."""
        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            mock_scraper = create_mock_scraper(sample_events_by_date)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()
            events = service.fetch_month(2026, 1, impact="high")

            assert len(events) == 1
            assert events[0].impact == Impact.HIGH


class TestCalendarServiceFetchToday:
    """Tests for the fetch_today method."""

    def test_fetch_today_scrapes_when_no_cache(self, mock_get_session):
        """Test that fetch_today scrapes when no cached data exists."""
        today = date.today()
        today_event = EconomicEvent(
            date=today,
            time=time(8, 30),
            currency="USD",
            impact=Impact.HIGH,
            event_name="Test Event",
            actual=None,
            forecast="100",
            previous="95",
        )

        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_scraper.fetch_day.return_value = [today_event]
            mock_scraper.__enter__ = MagicMock(return_value=mock_scraper)
            mock_scraper.__exit__ = MagicMock(return_value=False)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()
            events = service.fetch_today()

            mock_scraper.fetch_day.assert_called_once_with(today)
            assert len(events) == 1

    def test_fetch_today_applies_high_impact_filter(self, mock_get_session):
        """Test that high_impact_only filter is applied correctly."""
        today = date.today()
        today_events = [
            EconomicEvent(
                date=today,
                time=time(8, 30),
                currency="USD",
                impact=Impact.HIGH,
                event_name="High Impact Event",
                actual=None,
                forecast="100",
                previous="95",
            ),
            EconomicEvent(
                date=today,
                time=time(10, 0),
                currency="EUR",
                impact=Impact.LOW,
                event_name="Low Impact Event",
                actual=None,
                forecast="50",
                previous="45",
            ),
        ]

        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_scraper.fetch_day.return_value = today_events
            mock_scraper.__enter__ = MagicMock(return_value=mock_scraper)
            mock_scraper.__exit__ = MagicMock(return_value=False)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()
            events = service.fetch_today(high_impact_only=True)

            assert len(events) == 1
            assert events[0].impact == Impact.HIGH


class TestCalendarServiceStats:
    """Tests for the get_stats method."""

    def test_get_stats_returns_statistics(
        self, mock_get_session, sample_events_by_date
    ):
        """Test that get_stats returns correct statistics."""
        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            mock_scraper = create_mock_scraper(sample_events_by_date)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()

            # First populate the database
            service.fetch_month(2026, 1)

            # Then get stats
            stats = service.get_stats()

            assert stats["total_events"] == 2
            assert "USD" in stats["by_currency"]
            assert "EUR" in stats["by_currency"]
