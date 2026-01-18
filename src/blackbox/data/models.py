"""Pydantic models for economic calendar data.

This module defines the data structures used to represent
economic events and calendar data.
"""

from datetime import date
from datetime import time as dt_time
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field, field_validator

from blackbox.data.normalizer import normalize_value


class Impact(str, Enum):
    """Impact level of an economic event."""

    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    HOLIDAY = "holiday"
    UNKNOWN = "unknown"


class EconomicEvent(BaseModel):
    """Represents a single economic event from the calendar.

    Attributes:
        date: The date of the event.
        time: The time of the event (None if all day or tentative).
        currency: The currency affected (e.g., USD, EUR).
        impact: The expected impact level of the event.
        event_name: The name/title of the event.
        actual: The actual reported value (None if not yet released).
        forecast: The forecasted value (None if no forecast available).
        previous: The previous period's value (None if not available).
    """

    model_config = ConfigDict(frozen=True)

    date: date
    time: dt_time | None = None
    currency: str = Field(..., min_length=2, max_length=5)
    impact: Impact = Impact.UNKNOWN
    event_name: str = Field(..., min_length=1)
    actual: float | None = None
    forecast: float | None = None
    previous: float | None = None
    actual_raw: str | None = Field(default=None, exclude=True)
    forecast_raw: str | None = Field(default=None, exclude=True)
    previous_raw: str | None = Field(default=None, exclude=True)

    @field_validator("actual", "forecast", "previous", mode="before")
    @classmethod
    def normalize_economic_value(cls, v: str | float | None) -> float | None:
        """Normalize economic values from string to float.

        Converts values like "223K" to 223000, "2.5%" to 0.025, etc.
        """
        if v is None:
            return None
        if isinstance(v, (int, float)):
            return float(v)
        return normalize_value(v)


class CalendarDay(BaseModel):
    """Represents all economic events for a single day.

    Attributes:
        date: The date represented.
        events: List of economic events for this day.
    """

    date: date
    events: list[EconomicEvent] = Field(default_factory=list)

    @property
    def high_impact_events(self) -> list[EconomicEvent]:
        """Return only high impact events for this day."""
        return [e for e in self.events if e.impact == Impact.HIGH]

    @property
    def has_high_impact(self) -> bool:
        """Check if the day has any high impact events."""
        return len(self.high_impact_events) > 0


class CalendarMonth(BaseModel):
    """Represents the economic calendar for a full month.

    Attributes:
        year: The year of the calendar month.
        month: The month (1-12).
        days: List of CalendarDay objects for the month.
    """

    year: int = Field(..., ge=2000, le=2100)
    month: int = Field(..., ge=1, le=12)
    days: list[CalendarDay] = Field(default_factory=list)

    @property
    def all_events(self) -> list[EconomicEvent]:
        """Return all events across all days in the month."""
        events = []
        for day in self.days:
            events.extend(day.events)
        return events

    @property
    def high_impact_events(self) -> list[EconomicEvent]:
        """Return all high impact events in the month."""
        return [e for e in self.all_events if e.impact == Impact.HIGH]

    def filter_by_currency(self, currencies: list[str]) -> list[EconomicEvent]:
        """Filter events by currency codes.

        Args:
            currencies: List of currency codes to filter by (e.g., ['USD', 'EUR']).

        Returns:
            List of events matching the specified currencies.
        """
        currencies_upper = [c.upper() for c in currencies]
        return [e for e in self.all_events if e.currency.upper() in currencies_upper]

    def filter_by_impact(self, min_impact: Impact) -> list[EconomicEvent]:
        """Filter events by minimum impact level.

        Args:
            min_impact: Minimum impact level to include.

        Returns:
            List of events at or above the specified impact level.
        """
        impact_order = {Impact.LOW: 1, Impact.MEDIUM: 2, Impact.HIGH: 3}
        min_level = impact_order.get(min_impact, 0)
        return [
            e for e in self.all_events if impact_order.get(e.impact, 0) >= min_level
        ]
