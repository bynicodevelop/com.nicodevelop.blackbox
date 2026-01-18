"""Tests for the data models."""

from datetime import date, time

import pytest
from pydantic import ValidationError

from blackbox.data.models import CalendarDay, CalendarMonth, EconomicEvent, Impact


class TestImpact:
    """Tests for the Impact enum."""

    def test_impact_values(self):
        """Test that all impact values are defined."""
        assert Impact.LOW.value == "low"
        assert Impact.MEDIUM.value == "medium"
        assert Impact.HIGH.value == "high"
        assert Impact.HOLIDAY.value == "holiday"
        assert Impact.UNKNOWN.value == "unknown"


class TestEconomicEvent:
    """Tests for the EconomicEvent model."""

    def test_create_event(self, sample_event: EconomicEvent):
        """Test creating an economic event."""
        assert sample_event.date == date(2026, 1, 18)
        assert sample_event.time == time(8, 30)
        assert sample_event.currency == "USD"
        assert sample_event.impact == Impact.HIGH
        assert sample_event.event_name == "Non-Farm Employment Change"
        assert sample_event.actual == "223K"
        assert sample_event.forecast == "215K"
        assert sample_event.previous == "212K"

    def test_create_event_minimal(self):
        """Test creating an event with minimal required fields."""
        event = EconomicEvent(
            date=date(2026, 1, 18),
            currency="EUR",
            event_name="Test Event",
        )
        assert event.time is None
        assert event.impact == Impact.UNKNOWN
        assert event.actual is None
        assert event.forecast is None
        assert event.previous is None

    def test_event_is_frozen(self, sample_event: EconomicEvent):
        """Test that event is immutable."""
        with pytest.raises(ValidationError):
            sample_event.currency = "EUR"

    def test_currency_validation(self):
        """Test currency field validation."""
        # Too short
        with pytest.raises(ValidationError):
            EconomicEvent(date=date(2026, 1, 18), currency="A", event_name="Test")

        # Too long
        with pytest.raises(ValidationError):
            EconomicEvent(date=date(2026, 1, 18), currency="USDJPY", event_name="Test")

    def test_event_name_required(self):
        """Test that event_name is required and non-empty."""
        with pytest.raises(ValidationError):
            EconomicEvent(date=date(2026, 1, 18), currency="USD", event_name="")


class TestCalendarDay:
    """Tests for the CalendarDay model."""

    def test_create_day(self, sample_calendar_day: CalendarDay):
        """Test creating a calendar day."""
        assert sample_calendar_day.date == date(2026, 1, 18)
        assert len(sample_calendar_day.events) == 3

    def test_empty_day(self):
        """Test creating an empty calendar day."""
        day = CalendarDay(date=date(2026, 1, 20))
        assert day.date == date(2026, 1, 20)
        assert day.events == []

    def test_high_impact_events(self, sample_calendar_day: CalendarDay):
        """Test filtering high impact events."""
        high_impact = sample_calendar_day.high_impact_events
        assert len(high_impact) == 1
        assert high_impact[0].event_name == "Non-Farm Employment Change"

    def test_has_high_impact(self, sample_calendar_day: CalendarDay):
        """Test has_high_impact property."""
        assert sample_calendar_day.has_high_impact is True

        empty_day = CalendarDay(date=date(2026, 1, 20))
        assert empty_day.has_high_impact is False


class TestCalendarMonth:
    """Tests for the CalendarMonth model."""

    def test_create_month(self, sample_calendar_month: CalendarMonth):
        """Test creating a calendar month."""
        assert sample_calendar_month.year == 2026
        assert sample_calendar_month.month == 1
        assert len(sample_calendar_month.days) == 2

    def test_all_events(self, sample_calendar_month: CalendarMonth):
        """Test getting all events in the month."""
        all_events = sample_calendar_month.all_events
        assert len(all_events) == 4

    def test_high_impact_events(self, sample_calendar_month: CalendarMonth):
        """Test filtering high impact events for the month."""
        high_impact = sample_calendar_month.high_impact_events
        assert len(high_impact) == 1

    def test_filter_by_currency(self, sample_calendar_month: CalendarMonth):
        """Test filtering events by currency."""
        usd_events = sample_calendar_month.filter_by_currency(["USD"])
        assert len(usd_events) == 2
        assert all(e.currency == "USD" for e in usd_events)

        usd_eur_events = sample_calendar_month.filter_by_currency(["USD", "EUR"])
        assert len(usd_eur_events) == 3

        # Case insensitive
        usd_lower = sample_calendar_month.filter_by_currency(["usd"])
        assert len(usd_lower) == 2

    def test_filter_by_impact(self, sample_calendar_month: CalendarMonth):
        """Test filtering events by minimum impact level."""
        high_events = sample_calendar_month.filter_by_impact(Impact.HIGH)
        assert len(high_events) == 1

        medium_events = sample_calendar_month.filter_by_impact(Impact.MEDIUM)
        assert len(medium_events) == 2  # Medium + High

        low_events = sample_calendar_month.filter_by_impact(Impact.LOW)
        assert len(low_events) == 3  # Low + Medium + High (excluding Holiday)

    def test_year_validation(self):
        """Test year field validation."""
        with pytest.raises(ValidationError):
            CalendarMonth(year=1999, month=1)

        with pytest.raises(ValidationError):
            CalendarMonth(year=2101, month=1)

    def test_month_validation(self):
        """Test month field validation."""
        with pytest.raises(ValidationError):
            CalendarMonth(year=2026, month=0)

        with pytest.raises(ValidationError):
            CalendarMonth(year=2026, month=13)
