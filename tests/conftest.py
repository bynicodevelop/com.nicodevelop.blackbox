"""Pytest configuration and fixtures for Blackbox tests."""

import pytest
from click.testing import CliRunner
from fastapi.testclient import TestClient

from blackbox.api.main import app
from blackbox.cli.main import cli


@pytest.fixture
def cli_runner() -> CliRunner:
    """Provide a Click CLI test runner."""
    return CliRunner()


@pytest.fixture
def api_client() -> TestClient:
    """Provide a FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def cli_command():
    """Provide the CLI command group."""
    return cli
