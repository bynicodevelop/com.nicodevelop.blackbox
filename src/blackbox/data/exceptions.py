"""Custom exceptions for the data module.

This module defines exception classes for handling errors
during data fetching and scraping operations.
"""


class DataModuleError(Exception):
    """Base exception for all data module errors."""


class ScraperError(DataModuleError):
    """Base exception for scraper-related errors."""


class BrowserError(ScraperError):
    """Error related to browser/WebDriver operations."""


class BrowserInitializationError(BrowserError):
    """Failed to initialize the browser/WebDriver."""


class BrowserNavigationError(BrowserError):
    """Failed to navigate to the target URL."""


class PageLoadError(ScraperError):
    """Page failed to load within timeout."""


class ElementNotFoundError(ScraperError):
    """Expected element was not found on the page."""

    def __init__(self, selector: str, message: str | None = None):
        """Initialize with selector that failed to match.

        Args:
            selector: The CSS selector or identifier that was not found.
            message: Optional custom error message.
        """
        self.selector = selector
        default_message = f"Element not found: {selector}"
        super().__init__(message or default_message)


class ParsingError(ScraperError):
    """Failed to parse data from the page."""


class RateLimitError(ScraperError):
    """Request was rate limited by the target server."""


class BlockedError(ScraperError):
    """Request was blocked (Cloudflare, CAPTCHA, etc.)."""


class InvalidDateError(DataModuleError):
    """Invalid date provided for calendar lookup."""


class ConfigurationError(DataModuleError):
    """Invalid or missing configuration."""
