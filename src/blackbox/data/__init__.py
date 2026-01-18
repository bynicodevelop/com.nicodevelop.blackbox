"""Data module for Blackbox Trading Robot.

This module provides data fetching capabilities including
economic calendar scraping from various sources.
"""

from blackbox.data.models import (
    CalendarDay,
    CalendarMonth,
    EconomicEvent,
    Impact,
)
from blackbox.data.scraper.forex_factory import ForexFactoryScraper

__all__ = [
    "EconomicEvent",
    "CalendarDay",
    "CalendarMonth",
    "Impact",
    "ForexFactoryScraper",
]
