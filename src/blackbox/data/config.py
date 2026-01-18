"""Configuration for data scraping operations.

This module defines configuration classes for browser management,
scraping delays, and specific scraper implementations.
"""

import random
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScraperDelays:
    """Configuration for scraper timing delays.

    Delays are randomized within min/max ranges to simulate
    human-like behavior and avoid detection.

    Attributes:
        page_load_min: Minimum wait after page load (seconds).
        page_load_max: Maximum wait after page load (seconds).
        action_min: Minimum wait between actions (seconds).
        action_max: Maximum wait between actions (seconds).
        pagination_min: Minimum wait between pagination (seconds).
        pagination_max: Maximum wait between pagination (seconds).
    """

    page_load_min: float = 2.0
    page_load_max: float = 4.0
    action_min: float = 0.5
    action_max: float = 1.5
    pagination_min: float = 3.0
    pagination_max: float = 6.0

    def get_page_load_delay(self) -> float:
        """Get a random page load delay within configured range."""
        return random.uniform(self.page_load_min, self.page_load_max)

    def get_action_delay(self) -> float:
        """Get a random action delay within configured range."""
        return random.uniform(self.action_min, self.action_max)

    def get_pagination_delay(self) -> float:
        """Get a random pagination delay within configured range."""
        return random.uniform(self.pagination_min, self.pagination_max)


@dataclass
class BrowserConfig:
    """Configuration for browser/WebDriver settings.

    Attributes:
        headless: Run browser in headless mode.
        user_agent: Custom user agent string (None for default).
        page_load_timeout: Timeout for page loads (seconds).
        implicit_wait: Implicit wait timeout (seconds).
        window_width: Browser window width.
        window_height: Browser window height.
    """

    headless: bool = True
    user_agent: Optional[str] = None
    page_load_timeout: int = 30
    implicit_wait: int = 10
    window_width: int = 1920
    window_height: int = 1080


@dataclass
class ForexFactoryConfig:
    """Configuration specific to Forex Factory scraper.

    Attributes:
        base_url: The base URL for Forex Factory calendar.
        delays: Timing delay configuration.
        browser: Browser configuration.
        max_retries: Maximum retry attempts for failed requests.
        retry_delay: Base delay between retries (exponential backoff).
        cache_ttl: Cache time-to-live in seconds (0 to disable).
    """

    base_url: str = "https://www.forexfactory.com/calendar"
    delays: ScraperDelays = field(default_factory=ScraperDelays)
    browser: BrowserConfig = field(default_factory=BrowserConfig)
    max_retries: int = 3
    retry_delay: float = 5.0
    cache_ttl: int = 300


# Default configurations
DEFAULT_FOREX_FACTORY_CONFIG = ForexFactoryConfig()

# User agent pool for rotation
USER_AGENTS = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.2 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
]


def get_random_user_agent() -> str:
    """Get a random user agent from the pool."""
    return random.choice(USER_AGENTS)
