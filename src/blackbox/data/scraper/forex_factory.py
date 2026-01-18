"""Forex Factory calendar scraper implementation.

This module implements the scraper for fetching economic calendar
data from Forex Factory (https://www.forexfactory.com/calendar).
"""

import calendar
import re
from datetime import date, datetime, time, timedelta

from bs4 import BeautifulSoup
from tenacity import retry, stop_after_attempt, wait_exponential

from blackbox.core.logging import get_logger
from blackbox.data.config import ForexFactoryConfig
from blackbox.data.exceptions import ParsingError, ScraperError
from blackbox.data.models import CalendarDay, CalendarMonth, EconomicEvent, Impact
from blackbox.data.scraper.base import BaseScraper
from blackbox.data.scraper.browser import BrowserManager

logger = get_logger("blackbox.scraper.forex_factory")


# CSS selectors for Forex Factory calendar
SELECTORS = {
    "calendar_row": "tr.calendar__row",
    "date": "td.calendar__cell.calendar__date",
    "time": "td.calendar__cell.calendar__time",
    "currency": "td.calendar__cell.calendar__currency",
    "impact": "td.calendar__cell.calendar__impact",
    "event": "td.calendar__cell.calendar__event",
    "event_title": "span.calendar__event-title",
    "actual": "td.calendar__cell.calendar__actual",
    "forecast": "td.calendar__cell.calendar__forecast",
    "previous": "td.calendar__cell.calendar__previous",
    "impact_icon": "span.calendar__impact-icon",
}


class ForexFactoryScraper(BaseScraper):
    """Scraper for Forex Factory economic calendar.

    Fetches economic events including dates, times, currencies,
    impact levels, and actual/forecast/previous values.
    """

    def __init__(self, config: ForexFactoryConfig | None = None):
        """Initialize the Forex Factory scraper.

        Args:
            config: Scraper configuration (uses defaults if not provided).
        """
        self.config = config or ForexFactoryConfig()
        self._browser: BrowserManager | None = None

    @property
    def browser(self) -> BrowserManager:
        """Get or create the browser manager.

        Returns:
            BrowserManager instance.
        """
        if self._browser is None:
            self._browser = BrowserManager(
                config=self.config.browser,
                delays=self.config.delays,
            )
        return self._browser

    def _build_day_url(self, target_date: date) -> str:
        """Build the URL for a specific day's calendar.

        Args:
            target_date: The date to build the URL for.

        Returns:
            The full URL for the calendar day.
        """
        # Format: calendar?day=jan18.2026
        month_abbr = target_date.strftime("%b").lower()
        day = target_date.day
        year = target_date.year
        return f"{self.config.base_url}?day={month_abbr}{day}.{year}"

    def _parse_impact(self, cell: BeautifulSoup) -> Impact:
        """Parse the impact level from a calendar cell.

        Args:
            cell: BeautifulSoup element for the impact cell.

        Returns:
            Impact enum value.
        """
        icon = cell.select_one(SELECTORS["impact_icon"])
        if icon:
            icon_class = " ".join(icon.get("class", []))
            if "icon--ff-impact-red" in icon_class:
                return Impact.HIGH
            if "icon--ff-impact-ora" in icon_class:
                return Impact.MEDIUM
            if "icon--ff-impact-yel" in icon_class:
                return Impact.LOW
            if "icon--ff-impact-gra" in icon_class:
                return Impact.HOLIDAY

        return Impact.UNKNOWN

    def _parse_time(self, time_str: str, _event_date: date) -> time | None:
        """Parse time string to time object.

        Args:
            time_str: Time string from the calendar (e.g., "8:30am").
            _event_date: The date of the event (reserved for future use).

        Returns:
            time object or None if parsing fails or time is tentative.
        """
        time_str = time_str.strip().lower()

        # Handle special cases
        if not time_str or time_str in ["", "all day", "tentative", "day"]:
            return None

        # Parse time like "8:30am" or "2:00pm"
        try:
            # Try 12-hour format with am/pm
            match = re.match(r"(\d{1,2}):(\d{2})(am|pm)", time_str)
            if match:
                hour = int(match.group(1))
                minute = int(match.group(2))
                period = match.group(3)

                if period == "pm" and hour != 12:
                    hour += 12
                elif period == "am" and hour == 12:
                    hour = 0

                return time(hour, minute)
        except (ValueError, AttributeError):
            pass

        return None

    def _parse_value(self, cell: BeautifulSoup) -> str | None:
        """Parse a value cell (actual/forecast/previous).

        Args:
            cell: BeautifulSoup element for the value cell.

        Returns:
            String value or None if empty.
        """
        text = cell.get_text(strip=True)
        return text if text else None

    def _parse_calendar_page(
        self,
        html: str,
        target_date: date,
    ) -> list[EconomicEvent]:
        """Parse the calendar page HTML into events.

        Args:
            html: Raw HTML of the calendar page.
            target_date: The date we're fetching events for.

        Returns:
            List of EconomicEvent objects.

        Raises:
            ParsingError: If parsing fails.
        """
        try:
            soup = BeautifulSoup(html, "lxml")
            rows = soup.select(SELECTORS["calendar_row"])

            events = []
            current_date = target_date
            current_time: time | None = None

            for row in rows:
                # Check for date cell (some rows span multiple events)
                date_cell = row.select_one(SELECTORS["date"])
                if date_cell:
                    date_text = date_cell.get_text(strip=True)
                    if date_text:
                        # Parse date like "Jan 18" or just use target_date
                        try:
                            parsed = datetime.strptime(
                                f"{date_text} {target_date.year}",
                                "%b %d %Y",
                            )
                            current_date = parsed.date()
                        except ValueError:
                            pass

                # Check for time cell
                time_cell = row.select_one(SELECTORS["time"])
                if time_cell:
                    time_text = time_cell.get_text(strip=True)
                    if time_text:
                        current_time = self._parse_time(time_text, current_date)

                # Get currency
                currency_cell = row.select_one(SELECTORS["currency"])
                if not currency_cell:
                    continue
                currency = currency_cell.get_text(strip=True)
                if not currency:
                    continue

                # Get impact
                impact_cell = row.select_one(SELECTORS["impact"])
                impact = (
                    self._parse_impact(impact_cell) if impact_cell else Impact.UNKNOWN
                )

                # Get event name
                event_cell = row.select_one(SELECTORS["event"])
                if not event_cell:
                    continue
                title_elem = event_cell.select_one(SELECTORS["event_title"])
                event_name = (
                    title_elem.get_text(strip=True)
                    if title_elem
                    else event_cell.get_text(strip=True)
                )
                if not event_name:
                    continue

                # Get values
                actual_cell = row.select_one(SELECTORS["actual"])
                forecast_cell = row.select_one(SELECTORS["forecast"])
                previous_cell = row.select_one(SELECTORS["previous"])

                actual_raw = self._parse_value(actual_cell) if actual_cell else None
                forecast_raw = (
                    self._parse_value(forecast_cell) if forecast_cell else None
                )
                previous_raw = (
                    self._parse_value(previous_cell) if previous_cell else None
                )

                event = EconomicEvent(
                    date=current_date,
                    time=current_time,
                    currency=currency,
                    impact=impact,
                    event_name=event_name,
                    actual=actual_raw,
                    forecast=forecast_raw,
                    previous=previous_raw,
                    actual_raw=actual_raw,
                    forecast_raw=forecast_raw,
                    previous_raw=previous_raw,
                )
                events.append(event)

            logger.info(f"Parsed {len(events)} events for {target_date}")
            return events

        except Exception as e:
            logger.error(f"Failed to parse calendar page: {e}")
            raise ParsingError(f"Failed to parse calendar: {e}") from e

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=30),
        reraise=True,
    )
    def _fetch_day_with_retry(self, target_date: date) -> list[EconomicEvent]:
        """Fetch events for a day with retry logic.

        Args:
            target_date: The date to fetch events for.

        Returns:
            List of EconomicEvent objects.

        Raises:
            ScraperError: If fetching fails after retries.
        """
        url = self._build_day_url(target_date)
        logger.info(f"Fetching calendar for {target_date}: {url}")

        try:
            self.browser.navigate(url)
            html = self.browser.get_page_source()
            return self._parse_calendar_page(html, target_date)
        except ParsingError:
            raise
        except Exception as e:
            raise ScraperError(
                f"Failed to fetch calendar for {target_date}: {e}"
            ) from e

    def fetch_day(self, target_date: date) -> list[EconomicEvent]:
        """Fetch economic events for a single day.

        Args:
            target_date: The date to fetch events for.

        Returns:
            List of EconomicEvent objects for the specified date.

        Raises:
            ScraperError: If fetching fails.
        """
        return self._fetch_day_with_retry(target_date)

    def fetch_today(self) -> list[EconomicEvent]:
        """Fetch economic events for today.

        Returns:
            List of EconomicEvent objects for today.

        Raises:
            ScraperError: If fetching fails.
        """
        return self.fetch_day(date.today())

    def fetch_month(
        self,
        year: int,
        month: int,
        currencies: list[str] | None = None,
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
        logger.info(f"Starting fetch for {year}-{month:02d}")

        # Get number of days in the month
        _, num_days = calendar.monthrange(year, month)
        logger.info(f"Will fetch {num_days} days")

        days = []
        total_events = 0

        for day in range(1, num_days + 1):
            target_date = date(year, month, day)
            progress = (day / num_days) * 100

            logger.info(
                f"[{progress:5.1f}%] Fetching day {day}/{num_days}: {target_date}"
            )

            try:
                events = self.fetch_day(target_date)
                events_count = len(events)
                total_events += events_count

                # Filter by currencies if specified
                if currencies:
                    currencies_upper = [c.upper() for c in currencies]
                    events = [
                        e for e in events if e.currency.upper() in currencies_upper
                    ]
                    filtered_count = len(events)
                    logger.debug(
                        f"Filtered {events_count} -> {filtered_count} events (currencies: {currencies})"
                    )

                calendar_day = CalendarDay(date=target_date, events=events)
                days.append(calendar_day)

                logger.info(
                    f"[{progress:5.1f}%] Day {day}/{num_days} done: {len(events)} events"
                )

                # Add pagination delay between days (except last day)
                if day < num_days:
                    logger.debug("Waiting before next request...")
                    self.browser.pagination_delay()

            except ScraperError as e:
                logger.warning(f"[{progress:5.1f}%] Failed to fetch {target_date}: {e}")
                # Continue with empty day on error
                days.append(CalendarDay(date=target_date, events=[]))

        logger.info(
            f"Completed fetch for {year}-{month:02d}: {total_events} total events across {num_days} days"
        )
        return CalendarMonth(year=year, month=month, days=days)

    def fetch_range(
        self,
        start_date: date,
        end_date: date,
        currencies: list[str] | None = None,
    ) -> list[EconomicEvent]:
        """Fetch events for a date range.

        Args:
            start_date: Start of the range (inclusive).
            end_date: End of the range (inclusive).
            currencies: Optional list of currencies to filter by.

        Returns:
            List of EconomicEvent objects for the date range.

        Raises:
            ScraperError: If fetching fails.
        """
        events = []
        current = start_date

        while current <= end_date:
            try:
                day_events = self.fetch_day(current)

                # Filter by currencies if specified
                if currencies:
                    currencies_upper = [c.upper() for c in currencies]
                    day_events = [
                        e for e in day_events if e.currency.upper() in currencies_upper
                    ]

                events.extend(day_events)
                self.browser.pagination_delay()

            except ScraperError as e:
                logger.warning(f"Failed to fetch {current}: {e}")

            current += timedelta(days=1)

        return events

    def close(self) -> None:
        """Close the browser and clean up resources."""
        if self._browser is not None:
            self._browser.close()
            self._browser = None
