"""Browser manager using undetected-chromedriver.

This module provides a wrapper around undetected-chromedriver
with anti-detection features and human-like behavior simulation.
"""

import time
from typing import Optional

import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from blackbox.core.logging import get_logger
from blackbox.data.config import BrowserConfig, ScraperDelays, get_random_user_agent
from blackbox.data.exceptions import (
    BrowserInitializationError,
    BrowserNavigationError,
    ElementNotFoundError,
    PageLoadError,
)

logger = get_logger("blackbox.scraper.browser")


class BrowserManager:
    """Manages browser lifecycle and provides anti-detection features.

    This class wraps undetected-chromedriver and provides methods
    for human-like web interaction.
    """

    def __init__(
        self,
        config: Optional[BrowserConfig] = None,
        delays: Optional[ScraperDelays] = None,
    ):
        """Initialize the browser manager.

        Args:
            config: Browser configuration options.
            delays: Timing delay configuration.
        """
        self.config = config or BrowserConfig()
        self.delays = delays or ScraperDelays()
        self._driver: Optional[uc.Chrome] = None

    @property
    def driver(self) -> uc.Chrome:
        """Get or create the WebDriver instance.

        Returns:
            The Chrome WebDriver instance.

        Raises:
            BrowserInitializationError: If browser fails to initialize.
        """
        if self._driver is None:
            self._driver = self._create_driver()
        return self._driver

    def _create_driver(self) -> uc.Chrome:
        """Create and configure the Chrome WebDriver.

        Returns:
            Configured Chrome WebDriver instance.

        Raises:
            BrowserInitializationError: If browser fails to initialize.
        """
        try:
            logger.info("Initializing Chrome browser...")
            logger.debug(f"Headless mode: {self.config.headless}")

            options = uc.ChromeOptions()

            # Set user agent
            user_agent = self.config.user_agent or get_random_user_agent()
            options.add_argument(f"--user-agent={user_agent}")
            logger.debug(f"User-Agent: {user_agent[:50]}...")

            # Window size
            options.add_argument(
                f"--window-size={self.config.window_width},{self.config.window_height}"
            )

            # Anti-detection options
            options.add_argument("--disable-blink-features=AutomationControlled")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-gpu")
            options.add_argument("--disable-extensions")

            # Language and locale
            options.add_argument("--lang=en-US")
            options.add_argument("--accept-lang=en-US,en;q=0.9")

            logger.debug("Creating Chrome driver instance...")

            # Create driver
            driver = uc.Chrome(
                options=options,
                headless=self.config.headless,
            )

            # Set timeouts
            driver.set_page_load_timeout(self.config.page_load_timeout)
            driver.implicitly_wait(self.config.implicit_wait)
            logger.debug(f"Timeouts set: page_load={self.config.page_load_timeout}s, implicit={self.config.implicit_wait}s")

            logger.info("Browser initialized successfully")
            return driver

        except Exception as e:
            logger.error(f"Failed to initialize browser: {e}")
            raise BrowserInitializationError(f"Failed to initialize browser: {e}") from e

    def navigate(self, url: str) -> None:
        """Navigate to a URL with human-like delays.

        Args:
            url: The URL to navigate to.

        Raises:
            BrowserNavigationError: If navigation fails.
            PageLoadError: If page fails to load.
        """
        try:
            logger.debug(f"Navigating to: {url}")
            self.driver.get(url)

            # Wait for page load with random delay
            delay = self.delays.get_page_load_delay()
            time.sleep(delay)

            logger.debug(f"Page loaded after {delay:.2f}s delay")

        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            raise BrowserNavigationError(f"Failed to navigate to {url}: {e}") from e

    def wait_for_element(
        self,
        selector: str,
        by: By = By.CSS_SELECTOR,
        timeout: int = 10,
    ) -> WebElement:
        """Wait for an element to be present and visible.

        Args:
            selector: The selector to find the element.
            by: The selector type (default: CSS_SELECTOR).
            timeout: Maximum wait time in seconds.

        Returns:
            The found WebElement.

        Raises:
            ElementNotFoundError: If element is not found within timeout.
        """
        try:
            wait = WebDriverWait(self.driver, timeout)
            element = wait.until(EC.presence_of_element_located((by, selector)))
            return element
        except Exception:
            raise ElementNotFoundError(selector)

    def find_elements(
        self,
        selector: str,
        by: By = By.CSS_SELECTOR,
    ) -> list[WebElement]:
        """Find all elements matching the selector.

        Args:
            selector: The selector to find elements.
            by: The selector type (default: CSS_SELECTOR).

        Returns:
            List of matching WebElements (empty if none found).
        """
        return self.driver.find_elements(by, selector)

    def get_page_source(self) -> str:
        """Get the current page source.

        Returns:
            The HTML source of the current page.
        """
        return self.driver.page_source

    def human_delay(self) -> None:
        """Add a random human-like delay between actions."""
        delay = self.delays.get_action_delay()
        time.sleep(delay)

    def pagination_delay(self) -> None:
        """Add a random delay appropriate for pagination."""
        delay = self.delays.get_pagination_delay()
        time.sleep(delay)

    def close(self) -> None:
        """Close the browser and clean up resources."""
        if self._driver is not None:
            try:
                self._driver.quit()
                logger.info("Browser closed successfully")
            except Exception as e:
                logger.warning(f"Error closing browser: {e}")
            finally:
                self._driver = None

    def __enter__(self) -> "BrowserManager":
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit - ensure browser is closed."""
        self.close()
