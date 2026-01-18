"""Tests for API endpoints."""

from fastapi.testclient import TestClient

from blackbox import __version__
from blackbox.api.main import app


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
