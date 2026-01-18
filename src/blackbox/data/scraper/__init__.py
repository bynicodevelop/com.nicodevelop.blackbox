"""Scraper submodule for data fetching.

This module contains web scraping implementations for various
economic data sources.
"""

from blackbox.data.scraper.base import BaseScraper
from blackbox.data.scraper.browser import BrowserManager
from blackbox.data.scraper.forex_factory import ForexFactoryScraper

__all__ = [
    "BaseScraper",
    "BrowserManager",
    "ForexFactoryScraper",
]
