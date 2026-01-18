"""Tests for the CalendarService class."""

from datetime import date, time
from unittest.mock import MagicMock, patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from blackbox.data.models import CalendarDay, CalendarMonth, EconomicEvent, Impact
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
def sample_calendar_month():
    """Create a sample calendar month for scraper mock."""
    events = [
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
    ]
    days = [
        CalendarDay(
            date=date(2026, 1, 15),
            events=[e for e in events if e.date == date(2026, 1, 15)],
        ),
        CalendarDay(
            date=date(2026, 1, 16),
            events=[e for e in events if e.date == date(2026, 1, 16)],
        ),
    ]
    return CalendarMonth(year=2026, month=1, days=days)


class TestCalendarServiceFetchMonth:
    """Tests for the fetch_month method."""

    def test_fetch_month_scrapes_when_no_cache(
        self, mock_get_session, sample_calendar_month
    ):
        """Test that fetch_month scrapes when no cached data exists."""
        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            # Setup mock scraper
            mock_scraper = MagicMock()
            mock_scraper.fetch_month.return_value = sample_calendar_month
            mock_scraper.__enter__ = MagicMock(return_value=mock_scraper)
            mock_scraper.__exit__ = MagicMock(return_value=False)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()
            events = service.fetch_month(2026, 1)

            # Verify scraper was called
            mock_scraper.fetch_month.assert_called_once_with(2026, 1)
            assert len(events) == 2

    def test_fetch_month_uses_cache_when_data_exists(
        self, mock_get_session, sample_calendar_month
    ):
        """Test that fetch_month uses cache when data exists."""
        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            # Setup mock scraper
            mock_scraper = MagicMock()
            mock_scraper.fetch_month.return_value = sample_calendar_month
            mock_scraper.__enter__ = MagicMock(return_value=mock_scraper)
            mock_scraper.__exit__ = MagicMock(return_value=False)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()

            # First call - should scrape
            service.fetch_month(2026, 1)
            assert mock_scraper.fetch_month.call_count == 1

            # Second call - should use cache
            events = service.fetch_month(2026, 1)
            # Still only called once (used cache)
            assert mock_scraper.fetch_month.call_count == 1
            assert len(events) == 2

    def test_fetch_month_force_refresh_always_scrapes(
        self, mock_get_session, sample_calendar_month
    ):
        """Test that force_refresh always triggers scraping."""
        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            # Setup mock scraper
            mock_scraper = MagicMock()
            mock_scraper.fetch_month.return_value = sample_calendar_month
            mock_scraper.__enter__ = MagicMock(return_value=mock_scraper)
            mock_scraper.__exit__ = MagicMock(return_value=False)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()

            # First call - should scrape
            service.fetch_month(2026, 1)
            assert mock_scraper.fetch_month.call_count == 1

            # Second call with force_refresh - should scrape again
            service.fetch_month(2026, 1, force_refresh=True)
            assert mock_scraper.fetch_month.call_count == 2

    def test_fetch_month_applies_currency_filter(
        self, mock_get_session, sample_calendar_month
    ):
        """Test that currency filter is applied correctly."""
        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_scraper.fetch_month.return_value = sample_calendar_month
            mock_scraper.__enter__ = MagicMock(return_value=mock_scraper)
            mock_scraper.__exit__ = MagicMock(return_value=False)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()
            events = service.fetch_month(2026, 1, currencies=["USD"])

            assert len(events) == 1
            assert events[0].currency == "USD"

    def test_fetch_month_applies_impact_filter(
        self, mock_get_session, sample_calendar_month
    ):
        """Test that impact filter is applied correctly."""
        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_scraper.fetch_month.return_value = sample_calendar_month
            mock_scraper.__enter__ = MagicMock(return_value=mock_scraper)
            mock_scraper.__exit__ = MagicMock(return_value=False)
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
        self, mock_get_session, sample_calendar_month
    ):
        """Test that get_stats returns correct statistics."""
        with patch("blackbox.data.services.ForexFactoryScraper") as mock_scraper_class:
            mock_scraper = MagicMock()
            mock_scraper.fetch_month.return_value = sample_calendar_month
            mock_scraper.__enter__ = MagicMock(return_value=mock_scraper)
            mock_scraper.__exit__ = MagicMock(return_value=False)
            mock_scraper_class.return_value = mock_scraper

            service = CalendarService()

            # First populate the database
            service.fetch_month(2026, 1)

            # Then get stats
            stats = service.get_stats()

            assert stats["total_events"] == 2
            assert "USD" in stats["by_currency"]
            assert "EUR" in stats["by_currency"]
