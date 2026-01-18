"""Tests for CLI commands."""

from click.testing import CliRunner

from blackbox import __version__
from blackbox.cli.main import cli


def test_cli_help(cli_runner: CliRunner):
    """Test CLI help command."""
    result = cli_runner.invoke(cli, ["--help"])
    assert result.exit_code == 0
    assert "Blackbox Trading Robot CLI" in result.output


def test_cli_version(cli_runner: CliRunner):
    """Test CLI version command."""
    result = cli_runner.invoke(cli, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_cli_status(cli_runner: CliRunner):
    """Test CLI status command."""
    result = cli_runner.invoke(cli, ["status"])
    assert result.exit_code == 0
    assert "Blackbox Trading Robot" in result.output
    assert "Status: Ready" in result.output


def test_cli_run_dry(cli_runner: CliRunner):
    """Test CLI run command in dry-run mode."""
    result = cli_runner.invoke(cli, ["run", "--dry-run"])
    assert result.exit_code == 0
    assert "DRY RUN" in result.output


def test_cli_run_with_symbol(cli_runner: CliRunner):
    """Test CLI run command with custom symbol."""
    result = cli_runner.invoke(cli, ["run", "--symbol", "ETH/USDT", "--dry-run"])
    assert result.exit_code == 0
    assert "ETH/USDT" in result.output


def test_cli_backtest(cli_runner: CliRunner):
    """Test CLI backtest command."""
    result = cli_runner.invoke(cli, ["backtest", "test_strategy"])
    assert result.exit_code == 0
    assert "test_strategy" in result.output
