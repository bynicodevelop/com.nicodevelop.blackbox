"""Test fixtures for the data module tests."""

from datetime import date, time
from unittest.mock import MagicMock, patch

import pytest

from blackbox.data.config import BrowserConfig, ForexFactoryConfig, ScraperDelays
from blackbox.data.models import CalendarDay, CalendarMonth, EconomicEvent, Impact


@pytest.fixture
def sample_event() -> EconomicEvent:
    """Create a sample economic event for testing."""
    return EconomicEvent(
        date=date(2026, 1, 18),
        time=time(8, 30),
        currency="USD",
        impact=Impact.HIGH,
        event_name="Non-Farm Employment Change",
        actual="223K",
        forecast="215K",
        previous="212K",
    )


@pytest.fixture
def sample_events() -> list[EconomicEvent]:
    """Create a list of sample events for testing."""
    return [
        EconomicEvent(
            date=date(2026, 1, 18),
            time=time(8, 30),
            currency="USD",
            impact=Impact.HIGH,
            event_name="Non-Farm Employment Change",
            actual="223K",
            forecast="215K",
            previous="212K",
        ),
        EconomicEvent(
            date=date(2026, 1, 18),
            time=time(10, 0),
            currency="EUR",
            impact=Impact.MEDIUM,
            event_name="ECB President Speech",
            actual=None,
            forecast=None,
            previous=None,
        ),
        EconomicEvent(
            date=date(2026, 1, 18),
            time=time(14, 0),
            currency="USD",
            impact=Impact.LOW,
            event_name="Treasury Budget Statement",
            actual="-50B",
            forecast="-45B",
            previous="-40B",
        ),
        EconomicEvent(
            date=date(2026, 1, 19),
            time=None,
            currency="JPY",
            impact=Impact.HOLIDAY,
            event_name="Bank Holiday",
            actual=None,
            forecast=None,
            previous=None,
        ),
    ]


@pytest.fixture
def sample_calendar_day(sample_events: list[EconomicEvent]) -> CalendarDay:
    """Create a sample calendar day for testing."""
    day_events = [e for e in sample_events if e.date == date(2026, 1, 18)]
    return CalendarDay(date=date(2026, 1, 18), events=day_events)


@pytest.fixture
def sample_calendar_month(sample_events: list[EconomicEvent]) -> CalendarMonth:
    """Create a sample calendar month for testing."""
    day1 = CalendarDay(
        date=date(2026, 1, 18),
        events=[e for e in sample_events if e.date == date(2026, 1, 18)],
    )
    day2 = CalendarDay(
        date=date(2026, 1, 19),
        events=[e for e in sample_events if e.date == date(2026, 1, 19)],
    )
    return CalendarMonth(year=2026, month=1, days=[day1, day2])


@pytest.fixture
def default_config() -> ForexFactoryConfig:
    """Create a default configuration for testing."""
    return ForexFactoryConfig()


@pytest.fixture
def test_config() -> ForexFactoryConfig:
    """Create a test configuration with shorter delays."""
    return ForexFactoryConfig(
        delays=ScraperDelays(
            page_load_min=0.1,
            page_load_max=0.2,
            action_min=0.05,
            action_max=0.1,
            pagination_min=0.1,
            pagination_max=0.2,
        ),
        browser=BrowserConfig(headless=True),
    )


@pytest.fixture
def mock_browser():
    """Create a mock browser manager."""
    with patch("blackbox.data.scraper.forex_factory.BrowserManager") as mock:
        browser = MagicMock()
        browser.navigate = MagicMock()
        browser.get_page_source = MagicMock(return_value="<html></html>")
        browser.pagination_delay = MagicMock()
        browser.close = MagicMock()
        mock.return_value = browser
        yield browser


@pytest.fixture
def sample_html() -> str:
    """Return sample HTML for parsing tests."""
    return """
    <html>
    <body>
    <table class="calendar">
        <tr class="calendar__row">
            <td class="calendar__cell calendar__date"><span>Jan 18</span></td>
            <td class="calendar__cell calendar__time">8:30am</td>
            <td class="calendar__cell calendar__currency">USD</td>
            <td class="calendar__cell calendar__impact">
                <span class="calendar__impact-icon icon--ff-impact-red"></span>
            </td>
            <td class="calendar__cell calendar__event">
                <span class="calendar__event-title">Non-Farm Employment Change</span>
            </td>
            <td class="calendar__cell calendar__actual">223K</td>
            <td class="calendar__cell calendar__forecast">215K</td>
            <td class="calendar__cell calendar__previous">212K</td>
        </tr>
        <tr class="calendar__row">
            <td class="calendar__cell calendar__date"></td>
            <td class="calendar__cell calendar__time">10:00am</td>
            <td class="calendar__cell calendar__currency">EUR</td>
            <td class="calendar__cell calendar__impact">
                <span class="calendar__impact-icon icon--ff-impact-ora"></span>
            </td>
            <td class="calendar__cell calendar__event">
                <span class="calendar__event-title">ECB President Speech</span>
            </td>
            <td class="calendar__cell calendar__actual"></td>
            <td class="calendar__cell calendar__forecast"></td>
            <td class="calendar__cell calendar__previous"></td>
        </tr>
    </table>
    </body>
    </html>
    """
