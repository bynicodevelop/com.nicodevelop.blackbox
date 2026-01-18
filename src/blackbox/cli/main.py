"""CLI entry point for Blackbox Trading Robot.

This module defines the command-line interface using Click.
"""

import json
import logging
from datetime import date

import click

from blackbox import __version__
from blackbox.core.logging import setup_logging
from blackbox.data.config import BrowserConfig, ForexFactoryConfig
from blackbox.data.models import Impact
from blackbox.data.scraper.forex_factory import ForexFactoryScraper


@click.group()
@click.version_option(version=__version__, prog_name="blackbox")
@click.option("-v", "--verbose", is_flag=True, help="Enable verbose output (DEBUG level)")
@click.option("-q", "--quiet", is_flag=True, help="Quiet mode (WARNING level only)")
@click.pass_context
def cli(ctx: click.Context, verbose: bool, quiet: bool) -> None:
    """Blackbox Trading Robot CLI.

    A command-line interface for managing and running trading strategies.
    """
    # Determine log level
    if verbose:
        console_level = logging.DEBUG
    elif quiet:
        console_level = logging.WARNING
    else:
        console_level = logging.INFO

    # Initialize logging
    setup_logging(console_level=console_level)

    # Store in context for subcommands
    ctx.ensure_object(dict)
    ctx.obj["verbose"] = verbose
    ctx.obj["quiet"] = quiet


@cli.command()
def status() -> None:
    """Display the current status of the trading robot."""
    click.echo("Blackbox Trading Robot")
    click.echo(f"Version: {__version__}")
    click.echo("Status: Ready")


@cli.command()
@click.option("--symbol", "-s", default="BTC/USDT", help="Trading pair symbol")
@click.option("--dry-run", is_flag=True, help="Run in simulation mode")
def run(symbol: str, dry_run: bool) -> None:
    """Start the trading robot.

    Args:
        symbol: The trading pair to trade (e.g., BTC/USDT)
        dry_run: If True, run in simulation mode without real trades
    """
    mode = "DRY RUN" if dry_run else "LIVE"
    click.echo(f"Starting Blackbox Trading Robot [{mode}]")
    click.echo(f"Trading symbol: {symbol}")
    click.echo("Press Ctrl+C to stop")

    # TODO: Implement actual trading logic
    click.echo("Trading logic not yet implemented")


@cli.command()
@click.argument("strategy_name")
def backtest(strategy_name: str) -> None:
    """Run backtesting for a strategy.

    Args:
        strategy_name: Name of the strategy to backtest
    """
    click.echo(f"Running backtest for strategy: {strategy_name}")
    # TODO: Implement backtesting logic
    click.echo("Backtesting not yet implemented")


# Calendar commands group
@cli.group()
def calendar() -> None:
    """Economic calendar commands.

    Fetch and display economic events from Forex Factory.
    """


@calendar.command("fetch")
@click.option("--year", "-y", type=int, default=None, help="Year to fetch (default: current)")
@click.option("--month", "-m", type=int, default=None, help="Month to fetch (default: current)")
@click.option("--currency", "-c", multiple=True, help="Filter by currency (can be used multiple times)")
@click.option("--impact", "-i", type=click.Choice(["low", "medium", "high"]), help="Minimum impact level")
@click.option("--headless/--no-headless", default=True, help="Run browser in headless mode")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def calendar_fetch(
    year: int | None,
    month: int | None,
    currency: tuple,
    impact: str | None,
    headless: bool,
    json_output: bool,
) -> None:
    """Fetch economic calendar for a month.

    Examples:
        blackbox calendar fetch --year 2026 --month 1
        blackbox calendar fetch -c USD -c EUR --impact high
    """
    # Default to current month
    today = date.today()
    year = year or today.year
    month = month or today.month

    # Configure scraper
    config = ForexFactoryConfig(
        browser=BrowserConfig(headless=headless),
    )

    currencies = list(currency) if currency else None

    try:
        with ForexFactoryScraper(config) as scraper:
            calendar_month = scraper.fetch_month(year, month, currencies)

            # Filter by impact if specified
            events = calendar_month.all_events
            if impact:
                impact_enum = Impact(impact)
                events = calendar_month.filter_by_impact(impact_enum)

            if json_output:
                output = {
                    "year": year,
                    "month": month,
                    "events": [
                        {
                            "date": str(e.date),
                            "time": str(e.time) if e.time else None,
                            "currency": e.currency,
                            "impact": e.impact.value,
                            "event_name": e.event_name,
                            "actual": e.actual,
                            "forecast": e.forecast,
                            "previous": e.previous,
                        }
                        for e in events
                    ],
                }
                click.echo(json.dumps(output, indent=2))
            else:
                click.echo(f"\nFound {len(events)} events:\n")
                for event in events:
                    time_str = event.time.strftime("%H:%M") if event.time else "All Day"
                    impact_marker = {"high": "!!!", "medium": "!!", "low": "!", "holiday": "H", "unknown": "?"}
                    marker = impact_marker.get(event.impact.value, "?")
                    click.echo(
                        f"[{event.date}] [{time_str}] [{event.currency}] [{marker}] "
                        f"{event.event_name} | A:{event.actual or '-'} F:{event.forecast or '-'} P:{event.previous or '-'}"
                    )

    except Exception as e:
        click.echo(f"Error fetching calendar: {e}", err=True)
        raise click.Abort()


@calendar.command("today")
@click.option("--currency", "-c", multiple=True, help="Filter by currency")
@click.option("--high-impact-only", "-H", is_flag=True, help="Show only high impact events")
@click.option("--headless/--no-headless", default=True, help="Run browser in headless mode")
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def calendar_today(
    currency: tuple,
    high_impact_only: bool,
    headless: bool,
    json_output: bool,
) -> None:
    """Fetch today's economic calendar.

    Examples:
        blackbox calendar today
        blackbox calendar today -c USD --high-impact-only
    """
    config = ForexFactoryConfig(
        browser=BrowserConfig(headless=headless),
    )

    try:
        with ForexFactoryScraper(config) as scraper:
            events = scraper.fetch_today()

            # Filter by currencies
            if currency:
                currencies_upper = [c.upper() for c in currency]
                events = [e for e in events if e.currency.upper() in currencies_upper]

            # Filter by impact
            if high_impact_only:
                events = [e for e in events if e.impact == Impact.HIGH]

            if json_output:
                output = {
                    "date": str(date.today()),
                    "events": [
                        {
                            "time": str(e.time) if e.time else None,
                            "currency": e.currency,
                            "impact": e.impact.value,
                            "event_name": e.event_name,
                            "actual": e.actual,
                            "forecast": e.forecast,
                            "previous": e.previous,
                        }
                        for e in events
                    ],
                }
                click.echo(json.dumps(output, indent=2))
            else:
                click.echo(f"\nToday ({date.today()}) - {len(events)} events:\n")
                for event in events:
                    time_str = event.time.strftime("%H:%M") if event.time else "All Day"
                    impact_marker = {"high": "!!!", "medium": "!!", "low": "!", "holiday": "H", "unknown": "?"}
                    marker = impact_marker.get(event.impact.value, "?")
                    click.echo(
                        f"[{time_str}] [{event.currency}] [{marker}] "
                        f"{event.event_name} | A:{event.actual or '-'} F:{event.forecast or '-'} P:{event.previous or '-'}"
                    )

    except Exception as e:
        click.echo(f"Error fetching calendar: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    cli()
