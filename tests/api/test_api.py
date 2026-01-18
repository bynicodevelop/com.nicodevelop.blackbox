"""Tests for API endpoints."""

from unittest.mock import MagicMock, patch

from fastapi.testclient import TestClient

from blackbox import __version__


def test_root_endpoint(api_client: TestClient):
    """Test root endpoint returns API info."""
    response = api_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Blackbox Trading Robot API"
    assert data["version"] == __version__
    assert data["status"] == "running"


def test_health_endpoint(api_client: TestClient):
    """Test health check endpoint."""
    response = api_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"


def test_status_endpoint(api_client: TestClient):
    """Test status endpoint."""
    response = api_client.get("/api/v1/status")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ready"
    assert data["version"] == __version__
    assert "trading" in data
    assert "active_strategies" in data


def test_list_strategies(api_client: TestClient):
    """Test list strategies endpoint."""
    response = api_client.get("/api/v1/strategies")
    assert response.status_code == 200
    data = response.json()
    assert "strategies" in data


def test_start_strategy(api_client: TestClient):
    """Test start strategy endpoint."""
    response = api_client.post("/api/v1/strategies/test_strategy/start?dry_run=true")
    assert response.status_code == 200
    data = response.json()
    assert "test_strategy" in data["message"]
    assert data["dry_run"] is True


def test_stop_strategy(api_client: TestClient):
    """Test stop strategy endpoint."""
    response = api_client.post("/api/v1/strategies/test_strategy/stop")
    assert response.status_code == 200
    data = response.json()
    assert "test_strategy" in data["message"]


def test_openapi_docs(api_client: TestClient):
    """Test that OpenAPI docs are available."""
    response = api_client.get("/docs")
    assert response.status_code == 200


def test_redoc_docs(api_client: TestClient):
    """Test that ReDoc docs are available."""
    response = api_client.get("/redoc")
    assert response.status_code == 200


# Scoring API tests
class TestScoringAPI:
    """Tests for scoring API endpoints."""

    @patch("blackbox.api.main.get_session")
    def test_get_currency_score(
        self, mock_get_session: MagicMock, api_client: TestClient
    ):
        """Test currency score endpoint."""
        # Mock empty session (no events)
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        mock_get_session.return_value = mock_session

        response = api_client.get("/api/v1/scoring/currency/USD")

        assert response.status_code == 200
        data = response.json()
        assert data["currency"] == "USD"
        assert "score" in data
        assert "reference_time" in data
        assert "config" in data
        assert data["config"]["half_life_hours"] == 48.0
        assert data["config"]["lookback_days"] == 7

    @patch("blackbox.api.main.get_session")
    def test_get_currency_score_with_params(
        self, mock_get_session: MagicMock, api_client: TestClient
    ):
        """Test currency score endpoint with custom parameters."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        mock_get_session.return_value = mock_session

        response = api_client.get(
            "/api/v1/scoring/currency/EUR?half_life_hours=24&lookback_days=14"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["currency"] == "EUR"
        assert data["config"]["half_life_hours"] == 24.0
        assert data["config"]["lookback_days"] == 14

    @patch("blackbox.api.main.get_session")
    def test_get_currency_score_lowercase(
        self, mock_get_session: MagicMock, api_client: TestClient
    ):
        """Test currency is normalized to uppercase."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        mock_get_session.return_value = mock_session

        response = api_client.get("/api/v1/scoring/currency/usd")

        assert response.status_code == 200
        data = response.json()
        assert data["currency"] == "USD"

    @patch("blackbox.api.main.get_session")
    def test_get_pair_bias(self, mock_get_session: MagicMock, api_client: TestClient):
        """Test pair bias endpoint."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        mock_get_session.return_value = mock_session

        response = api_client.get("/api/v1/scoring/pair/EUR/USD")

        assert response.status_code == 200
        data = response.json()
        assert data["base"] == "EUR"
        assert data["quote"] == "USD"
        assert data["pair"] == "EURUSD"
        assert "base_score" in data
        assert "quote_score" in data
        assert "bias" in data
        assert "reference_time" in data

    @patch("blackbox.api.main.get_session")
    def test_get_pair_bias_lowercase(
        self, mock_get_session: MagicMock, api_client: TestClient
    ):
        """Test pair currencies are normalized to uppercase."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        mock_get_session.return_value = mock_session

        response = api_client.get("/api/v1/scoring/pair/eur/usd")

        assert response.status_code == 200
        data = response.json()
        assert data["base"] == "EUR"
        assert data["quote"] == "USD"
        assert data["pair"] == "EURUSD"

    @patch("blackbox.api.main.get_session")
    def test_get_pair_signal(self, mock_get_session: MagicMock, api_client: TestClient):
        """Test pair signal endpoint."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        mock_get_session.return_value = mock_session

        response = api_client.get("/api/v1/scoring/signal/EUR/USD")

        assert response.status_code == 200
        data = response.json()
        assert data["base"] == "EUR"
        assert data["quote"] == "USD"
        assert data["pair"] == "EURUSD"
        assert "bias" in data
        assert data["signal"] in ["BULLISH", "BEARISH", "NEUTRAL"]
        assert data["threshold"] == 1.0
        assert "reference_time" in data

    @patch("blackbox.api.main.get_session")
    def test_get_pair_signal_with_threshold(
        self, mock_get_session: MagicMock, api_client: TestClient
    ):
        """Test pair signal endpoint with custom threshold."""
        mock_session = MagicMock()
        mock_session.execute.return_value.scalars.return_value.all.return_value = []
        mock_get_session.return_value = mock_session

        response = api_client.get(
            "/api/v1/scoring/signal/EUR/USD?min_bias_threshold=2.5"
        )

        assert response.status_code == 200
        data = response.json()
        assert data["threshold"] == 2.5
        # With no events and high threshold, should be NEUTRAL
        assert data["signal"] == "NEUTRAL"

    def test_get_currency_score_invalid_half_life(self, api_client: TestClient):
        """Test invalid half_life_hours returns 422."""
        response = api_client.get("/api/v1/scoring/currency/USD?half_life_hours=0")
        assert response.status_code == 422

    def test_get_currency_score_negative_lookback(self, api_client: TestClient):
        """Test negative lookback_days returns 422."""
        response = api_client.get("/api/v1/scoring/currency/USD?lookback_days=-1")
        assert response.status_code == 422
