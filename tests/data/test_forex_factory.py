"""Tests for the Forex Factory scraper."""

from datetime import date, time
from unittest.mock import MagicMock, patch

import pytest

from blackbox.data.config import ForexFactoryConfig
from blackbox.data.exceptions import ParsingError
from blackbox.data.models import Impact
from blackbox.data.scraper.forex_factory import ForexFactoryScraper


class TestForexFactoryScraper:
    """Tests for the ForexFactoryScraper class."""

    def test_build_day_url(self, test_config: ForexFactoryConfig):
        """Test URL building for a specific day."""
        scraper = ForexFactoryScraper(test_config)

        url = scraper._build_day_url(date(2026, 1, 18))
        assert url == "https://www.forexfactory.com/calendar?day=jan18.2026"

        url = scraper._build_day_url(date(2026, 12, 5))
        assert url == "https://www.forexfactory.com/calendar?day=dec5.2026"

        scraper.close()

    def test_parse_impact_high(self, test_config: ForexFactoryConfig):
        """Test parsing high impact from HTML."""
        from bs4 import BeautifulSoup

        scraper = ForexFactoryScraper(test_config)

        html = '<td class="calendar__cell calendar__impact"><span class="calendar__impact-icon icon--ff-impact-red"></span></td>'
        soup = BeautifulSoup(html, "lxml")
        cell = soup.select_one("td")

        impact = scraper._parse_impact(cell)
        assert impact == Impact.HIGH

        scraper.close()

    def test_parse_impact_medium(self, test_config: ForexFactoryConfig):
        """Test parsing medium impact from HTML."""
        from bs4 import BeautifulSoup

        scraper = ForexFactoryScraper(test_config)

        html = '<td class="calendar__cell calendar__impact"><span class="calendar__impact-icon icon--ff-impact-ora"></span></td>'
        soup = BeautifulSoup(html, "lxml")
        cell = soup.select_one("td")

        impact = scraper._parse_impact(cell)
        assert impact == Impact.MEDIUM

        scraper.close()

    def test_parse_impact_low(self, test_config: ForexFactoryConfig):
        """Test parsing low impact from HTML."""
        from bs4 import BeautifulSoup

        scraper = ForexFactoryScraper(test_config)

        html = '<td class="calendar__cell calendar__impact"><span class="calendar__impact-icon icon--ff-impact-yel"></span></td>'
        soup = BeautifulSoup(html, "lxml")
        cell = soup.select_one("td")

        impact = scraper._parse_impact(cell)
        assert impact == Impact.LOW

        scraper.close()

    def test_parse_time_am(self, test_config: ForexFactoryConfig):
        """Test parsing AM time."""
        scraper = ForexFactoryScraper(test_config)

        result = scraper._parse_time("8:30am", date(2026, 1, 18))
        assert result == time(8, 30)

        result = scraper._parse_time("12:00am", date(2026, 1, 18))
        assert result == time(0, 0)

        scraper.close()

    def test_parse_time_pm(self, test_config: ForexFactoryConfig):
        """Test parsing PM time."""
        scraper = ForexFactoryScraper(test_config)

        result = scraper._parse_time("2:00pm", date(2026, 1, 18))
        assert result == time(14, 0)

        result = scraper._parse_time("12:30pm", date(2026, 1, 18))
        assert result == time(12, 30)

        scraper.close()

    def test_parse_time_special_cases(self, test_config: ForexFactoryConfig):
        """Test parsing special time cases."""
        scraper = ForexFactoryScraper(test_config)

        assert scraper._parse_time("", date(2026, 1, 18)) is None
        assert scraper._parse_time("all day", date(2026, 1, 18)) is None
        assert scraper._parse_time("tentative", date(2026, 1, 18)) is None
        assert scraper._parse_time("day", date(2026, 1, 18)) is None

        scraper.close()

    def test_parse_calendar_page(self, test_config: ForexFactoryConfig, sample_html: str):
        """Test parsing a calendar page."""
        scraper = ForexFactoryScraper(test_config)

        events = scraper._parse_calendar_page(sample_html, date(2026, 1, 18))

        assert len(events) == 2

        # First event
        assert events[0].currency == "USD"
        assert events[0].impact == Impact.HIGH
        assert events[0].event_name == "Non-Farm Employment Change"
        assert events[0].actual == "223K"
        assert events[0].forecast == "215K"
        assert events[0].previous == "212K"

        # Second event
        assert events[1].currency == "EUR"
        assert events[1].impact == Impact.MEDIUM
        assert events[1].event_name == "ECB President Speech"
        assert events[1].actual is None

        scraper.close()

    def test_parse_calendar_page_empty(self, test_config: ForexFactoryConfig):
        """Test parsing an empty calendar page."""
        scraper = ForexFactoryScraper(test_config)

        html = "<html><body><table></table></body></html>"
        events = scraper._parse_calendar_page(html, date(2026, 1, 18))

        assert events == []

        scraper.close()

    @patch("blackbox.data.scraper.forex_factory.BrowserManager")
    def test_fetch_day(self, mock_browser_class, test_config: ForexFactoryConfig, sample_html: str):
        """Test fetching a day's events."""
        mock_browser = MagicMock()
        mock_browser.navigate = MagicMock()
        mock_browser.get_page_source = MagicMock(return_value=sample_html)
        mock_browser.pagination_delay = MagicMock()
        mock_browser.close = MagicMock()
        mock_browser_class.return_value = mock_browser

        scraper = ForexFactoryScraper(test_config)
        events = scraper.fetch_day(date(2026, 1, 18))

        assert len(events) == 2
        mock_browser.navigate.assert_called_once()
        mock_browser.get_page_source.assert_called_once()

        scraper.close()

    @patch("blackbox.data.scraper.forex_factory.BrowserManager")
    def test_fetch_today(self, mock_browser_class, test_config: ForexFactoryConfig, sample_html: str):
        """Test fetching today's events."""
        mock_browser = MagicMock()
        mock_browser.navigate = MagicMock()
        mock_browser.get_page_source = MagicMock(return_value=sample_html)
        mock_browser.close = MagicMock()
        mock_browser_class.return_value = mock_browser

        scraper = ForexFactoryScraper(test_config)
        events = scraper.fetch_today()

        assert len(events) == 2

        scraper.close()

    @patch("blackbox.data.scraper.forex_factory.BrowserManager")
    def test_context_manager(self, mock_browser_class, test_config: ForexFactoryConfig, sample_html: str):
        """Test using scraper as context manager."""
        mock_browser = MagicMock()
        mock_browser.navigate = MagicMock()
        mock_browser.get_page_source = MagicMock(return_value=sample_html)
        mock_browser.close = MagicMock()
        mock_browser_class.return_value = mock_browser

        with ForexFactoryScraper(test_config) as scraper:
            events = scraper.fetch_day(date(2026, 1, 18))
            assert len(events) == 2

        # Browser should be closed after context exit
        mock_browser.close.assert_called()

    def test_default_config(self):
        """Test scraper with default config."""
        scraper = ForexFactoryScraper()
        assert scraper.config.base_url == "https://www.forexfactory.com/calendar"
        scraper.close()
