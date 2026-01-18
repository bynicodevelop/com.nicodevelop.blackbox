"""High-level services for calendar data management.

This module provides services that orchestrate between
the scraper and the database repository for intelligent
caching and data management.
"""

import calendar as cal
from datetime import date

from blackbox.core.logging import get_logger
from blackbox.data.config import ForexFactoryConfig
from blackbox.data.models import EconomicEvent, Impact
from blackbox.data.scraper.forex_factory import ForexFactoryScraper
from blackbox.data.storage.database import get_session
from blackbox.data.storage.repository import EventRepository

logger = get_logger("blackbox.services")


class CalendarService:
    """Service for managing economic calendar data with intelligent caching.

    Orchestrates between the scraper and database repository to provide
    efficient data fetching with automatic caching.
    """

    def __init__(
        self,
        config: ForexFactoryConfig | None = None,
    ):
        """Initialize the calendar service.

        Args:
            config: Optional scraper configuration.
        """
        self.config = config or ForexFactoryConfig()

    def fetch_month(
        self,
        year: int,
        month: int,
        currencies: list[str] | None = None,
        impact: str | None = None,
        force_refresh: bool = False,
    ) -> list[EconomicEvent]:
        """Fetch economic events for a month with intelligent caching.

        If force_refresh is False:
        1. Check if events exist in database
        2. If yes, check for events needing updates (actual IS NULL)
        3. Only scrape dates with missing data
        4. Return complete data from repository

        If force_refresh is True:
        1. Scrape the entire month
        2. Upsert all events to database
        3. Return fresh data

        Args:
            year: The year to fetch.
            month: The month to fetch (1-12).
            currencies: Optional list of currencies to filter by.
            impact: Optional minimum impact level.
            force_refresh: If True, ignore cache and scrape everything.

        Returns:
            List of EconomicEvent objects.
        """
        _, last_day = cal.monthrange(year, month)
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        with get_session() as session:
            repo = EventRepository(session)

            if force_refresh:
                logger.info(f"Force refresh requested for {year}-{month:02d}")
                events = self._scrape_and_store_month(year, month, repo)
            else:
                # Check if we have data
                has_data = repo.has_events_for_month(year, month)

                if not has_data:
                    logger.info(f"No cached data for {year}-{month:02d}, scraping...")
                    events = self._scrape_and_store_month(year, month, repo)
                else:
                    # Check for events needing updates
                    dates_to_update = repo.get_events_needing_update(
                        start_date, end_date
                    )

                    if dates_to_update:
                        logger.info(
                            f"Found {len(dates_to_update)} dates needing updates"
                        )
                        self._scrape_and_store_dates(dates_to_update, repo)

                    # Return from cache
                    logger.info(f"Returning cached data for {year}-{month:02d}")
                    events = repo.get_events(start_date, end_date, currencies, impact)

            # Apply filters if we just scraped (filters not applied during scrape)
            if force_refresh or not has_data:
                events = repo.get_events(start_date, end_date, currencies, impact)

            return events

    def fetch_today(
        self,
        currencies: list[str] | None = None,
        high_impact_only: bool = False,
    ) -> list[EconomicEvent]:
        """Fetch today's economic events with caching.

        Args:
            currencies: Optional list of currencies to filter by.
            high_impact_only: If True, only return high impact events.

        Returns:
            List of EconomicEvent objects for today.
        """
        today = date.today()

        with get_session() as session:
            repo = EventRepository(session)

            # Check if we have data for today
            events = repo.get_events_for_date(today)

            if not events:
                logger.info("No cached data for today, scraping...")
                events = self._scrape_and_store_day(today, repo)

            # Apply filters
            if currencies:
                currencies_upper = [c.upper() for c in currencies]
                events = [e for e in events if e.currency.upper() in currencies_upper]

            if high_impact_only:
                events = [e for e in events if e.impact == Impact.HIGH]

            return events

    def refresh_month(self, year: int, month: int) -> int:
        """Force refresh all events for a month.

        Args:
            year: The year to refresh.
            month: The month to refresh.

        Returns:
            Number of events upserted.
        """
        with get_session() as session:
            repo = EventRepository(session)
            return self._scrape_and_store_month(year, month, repo, return_count=True)

    def get_stats(self) -> dict:
        """Get statistics about stored events.

        Returns:
            Dictionary with statistics.
        """
        with get_session() as session:
            repo = EventRepository(session)
            return repo.get_stats()

    def _scrape_and_store_month(
        self,
        year: int,
        month: int,
        repo: EventRepository,
        return_count: bool = False,
    ) -> list[EconomicEvent] | int:
        """Scrape a full month and store in database.

        Args:
            year: The year to scrape.
            month: The month to scrape.
            repo: Repository instance.
            return_count: If True, return count instead of events.

        Returns:
            List of events or count if return_count is True.
        """
        with ForexFactoryScraper(self.config) as scraper:
            calendar_month = scraper.fetch_month(year, month)
            events = calendar_month.all_events

            count = repo.upsert_events(events)
            logger.info(f"Upserted {count} events for {year}-{month:02d}")

            if return_count:
                return count
            return events

    def _scrape_and_store_dates(
        self,
        dates: list[date],
        repo: EventRepository,
    ) -> int:
        """Scrape specific dates and store in database.

        Args:
            dates: List of dates to scrape.
            repo: Repository instance.

        Returns:
            Number of events upserted.
        """
        total_count = 0

        with ForexFactoryScraper(self.config) as scraper:
            for target_date in dates:
                events = scraper.fetch_day(target_date)
                count = repo.upsert_events(events)
                total_count += count
                logger.info(f"Upserted {count} events for {target_date}")

        return total_count

    def _scrape_and_store_day(
        self,
        target_date: date,
        repo: EventRepository,
    ) -> list[EconomicEvent]:
        """Scrape a single day and store in database.

        Args:
            target_date: The date to scrape.
            repo: Repository instance.

        Returns:
            List of scraped events.
        """
        with ForexFactoryScraper(self.config) as scraper:
            events = scraper.fetch_day(target_date)
            count = repo.upsert_events(events)
            logger.info(f"Upserted {count} events for {target_date}")
            return events
