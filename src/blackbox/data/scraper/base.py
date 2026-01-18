"""Base scraper abstract class.

This module defines the interface that all scrapers must implement.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Optional

from blackbox.data.models import CalendarMonth, EconomicEvent


class BaseScraper(ABC):
    """Abstract base class for all calendar scrapers.

    Defines the interface that scraper implementations must follow.
    """

    @abstractmethod
    def fetch_month(
        self,
        year: int,
        month: int,
        currencies: Optional[list[str]] = None,
    ) -> CalendarMonth:
        """Fetch the economic calendar for a full month.

        Args:
            year: The year to fetch.
            month: The month to fetch (1-12).
            currencies: Optional list of currencies to filter by.

        Returns:
            CalendarMonth containing all events for the specified month.

        Raises:
            ScraperError: If fetching fails.
        """

    @abstractmethod
    def fetch_day(self, target_date: date) -> list[EconomicEvent]:
        """Fetch economic events for a single day.

        Args:
            target_date: The date to fetch events for.

        Returns:
            List of EconomicEvent objects for the specified date.

        Raises:
            ScraperError: If fetching fails.
        """

    @abstractmethod
    def fetch_today(self) -> list[EconomicEvent]:
        """Fetch economic events for today.

        Returns:
            List of EconomicEvent objects for today.

        Raises:
            ScraperError: If fetching fails.
        """

    @abstractmethod
    def close(self) -> None:
        """Clean up resources (close browser, etc.)."""

    def __enter__(self) -> "BaseScraper":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - ensure cleanup."""
        self.close()
