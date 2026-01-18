"""Tests for the configuration module."""

from blackbox.data.config import (
    USER_AGENTS,
    BrowserConfig,
    ForexFactoryConfig,
    ScraperDelays,
    get_random_user_agent,
)


class TestScraperDelays:
    """Tests for the ScraperDelays configuration."""

    def test_default_values(self):
        """Test default delay values."""
        delays = ScraperDelays()
        assert delays.page_load_min == 2.0
        assert delays.page_load_max == 4.0
        assert delays.action_min == 0.5
        assert delays.action_max == 1.5
        assert delays.pagination_min == 3.0
        assert delays.pagination_max == 6.0

    def test_custom_values(self):
        """Test custom delay values."""
        delays = ScraperDelays(
            page_load_min=1.0,
            page_load_max=2.0,
            action_min=0.1,
            action_max=0.5,
        )
        assert delays.page_load_min == 1.0
        assert delays.page_load_max == 2.0
        assert delays.action_min == 0.1
        assert delays.action_max == 0.5

    def test_get_page_load_delay(self):
        """Test page load delay generation."""
        delays = ScraperDelays(page_load_min=1.0, page_load_max=2.0)

        for _ in range(100):
            delay = delays.get_page_load_delay()
            assert 1.0 <= delay <= 2.0

    def test_get_action_delay(self):
        """Test action delay generation."""
        delays = ScraperDelays(action_min=0.5, action_max=1.0)

        for _ in range(100):
            delay = delays.get_action_delay()
            assert 0.5 <= delay <= 1.0

    def test_get_pagination_delay(self):
        """Test pagination delay generation."""
        delays = ScraperDelays(pagination_min=2.0, pagination_max=3.0)

        for _ in range(100):
            delay = delays.get_pagination_delay()
            assert 2.0 <= delay <= 3.0


class TestBrowserConfig:
    """Tests for the BrowserConfig configuration."""

    def test_default_values(self):
        """Test default browser config values."""
        config = BrowserConfig()
        assert config.headless is True
        assert config.user_agent is None
        assert config.page_load_timeout == 30
        assert config.implicit_wait == 10
        assert config.window_width == 1920
        assert config.window_height == 1080

    def test_custom_values(self):
        """Test custom browser config values."""
        config = BrowserConfig(
            headless=False,
            user_agent="Custom Agent",
            page_load_timeout=60,
        )
        assert config.headless is False
        assert config.user_agent == "Custom Agent"
        assert config.page_load_timeout == 60


class TestForexFactoryConfig:
    """Tests for the ForexFactoryConfig configuration."""

    def test_default_values(self):
        """Test default Forex Factory config values."""
        config = ForexFactoryConfig()
        assert config.base_url == "https://www.forexfactory.com/calendar"
        assert config.max_retries == 3
        assert config.retry_delay == 5.0
        assert config.cache_ttl == 300
        assert isinstance(config.delays, ScraperDelays)
        assert isinstance(config.browser, BrowserConfig)

    def test_custom_values(self):
        """Test custom Forex Factory config values."""
        delays = ScraperDelays(page_load_min=1.0, page_load_max=2.0)
        browser = BrowserConfig(headless=False)

        config = ForexFactoryConfig(
            base_url="https://custom.url.com",
            delays=delays,
            browser=browser,
            max_retries=5,
        )
        assert config.base_url == "https://custom.url.com"
        assert config.delays.page_load_min == 1.0
        assert config.browser.headless is False
        assert config.max_retries == 5


class TestUserAgents:
    """Tests for user agent utilities."""

    def test_user_agents_list(self):
        """Test that user agents list is populated."""
        assert len(USER_AGENTS) > 0
        for agent in USER_AGENTS:
            assert isinstance(agent, str)
            assert len(agent) > 0

    def test_get_random_user_agent(self):
        """Test random user agent selection."""
        agents = set()
        for _ in range(100):
            agent = get_random_user_agent()
            assert agent in USER_AGENTS
            agents.add(agent)

        # Should have selected multiple different agents
        assert len(agents) > 1
