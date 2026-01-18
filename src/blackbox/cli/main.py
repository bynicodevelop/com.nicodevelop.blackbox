"""CLI entry point for Blackbox Trading Robot.

This module defines the command-line interface using Click.
"""

import csv
import json
import logging
from datetime import date
from io import StringIO

import click

from blackbox import __version__
from blackbox.core.logging import setup_logging
from blackbox.data.config import BrowserConfig, ForexFactoryConfig
from blackbox.data.services import CalendarService
from blackbox.data.storage.database import get_session, init_db
from blackbox.data.storage.repository import EventRepository


@click.group()
@click.version_option(version=__version__, prog_name="blackbox")
@click.option(
    "-v", "--verbose", is_flag=True, help="Enable verbose output (DEBUG level)"
)
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
@click.option(
    "--year", "-y", type=int, default=None, help="Year to fetch (default: current)"
)
@click.option(
    "--month", "-m", type=int, default=None, help="Month to fetch (default: current)"
)
@click.option(
    "--currency",
    "-c",
    multiple=True,
    help="Filter by currency (can be used multiple times)",
)
@click.option(
    "--impact",
    "-i",
    type=click.Choice(["low", "medium", "high"]),
    help="Minimum impact level",
)
@click.option(
    "--headless/--no-headless", default=True, help="Run browser in headless mode"
)
@click.option(
    "--force-refresh", "-f", is_flag=True, help="Force scraping even if data is cached"
)
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def calendar_fetch(
    year: int | None,
    month: int | None,
    currency: tuple,
    impact: str | None,
    headless: bool,
    force_refresh: bool,
    json_output: bool,
) -> None:
    """Fetch economic calendar for a month.

    Uses cached data from PostgreSQL when available.
    Use --force-refresh to always scrape fresh data.

    Examples:
        blackbox calendar fetch --year 2026 --month 1
        blackbox calendar fetch -c USD -c EUR --impact high
        blackbox calendar fetch --force-refresh
    """
    # Default to current month
    today = date.today()
    year = year or today.year
    month = month or today.month

    # Configure service
    config = ForexFactoryConfig(
        browser=BrowserConfig(headless=headless),
    )

    currencies = list(currency) if currency else None

    try:
        service = CalendarService(config)
        events = service.fetch_month(year, month, currencies, impact, force_refresh)

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
                impact_marker = {
                    "high": "!!!",
                    "medium": "!!",
                    "low": "!",
                    "holiday": "H",
                    "unknown": "?",
                }
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
@click.option(
    "--high-impact-only", "-H", is_flag=True, help="Show only high impact events"
)
@click.option(
    "--headless/--no-headless", default=True, help="Run browser in headless mode"
)
@click.option("--json-output", "-j", is_flag=True, help="Output as JSON")
def calendar_today(
    currency: tuple,
    high_impact_only: bool,
    headless: bool,
    json_output: bool,
) -> None:
    """Fetch today's economic calendar.

    Uses cached data from PostgreSQL when available.

    Examples:
        blackbox calendar today
        blackbox calendar today -c USD --high-impact-only
    """
    config = ForexFactoryConfig(
        browser=BrowserConfig(headless=headless),
    )

    currencies = list(currency) if currency else None

    try:
        service = CalendarService(config)
        events = service.fetch_today(currencies, high_impact_only)

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
                impact_marker = {
                    "high": "!!!",
                    "medium": "!!",
                    "low": "!",
                    "holiday": "H",
                    "unknown": "?",
                }
                marker = impact_marker.get(event.impact.value, "?")
                click.echo(
                    f"[{time_str}] [{event.currency}] [{marker}] "
                    f"{event.event_name} | A:{event.actual or '-'} F:{event.forecast or '-'} P:{event.previous or '-'}"
                )

    except Exception as e:
        click.echo(f"Error fetching calendar: {e}", err=True)
        raise click.Abort()


# Database commands group
@cli.group()
def db() -> None:
    """Database management commands.

    Initialize, inspect, and export calendar data from PostgreSQL.
    """


@db.command("init")
def db_init() -> None:
    """Initialize the database tables.

    Creates all required tables in PostgreSQL.

    Examples:
        blackbox db init
    """
    try:
        init_db()
        click.echo("Database tables created successfully.")
    except Exception as e:
        click.echo(f"Error initializing database: {e}", err=True)
        raise click.Abort()


@db.command("stats")
def db_stats() -> None:
    """Display statistics about stored events.

    Shows total events, counts by currency and impact level,
    and date range of stored data.

    Examples:
        blackbox db stats
    """
    try:
        service = CalendarService()
        stats = service.get_stats()

        click.echo("\nDatabase Statistics\n" + "=" * 40)
        click.echo(f"Total events: {stats['total_events']}")

        if stats["date_range"][0]:
            click.echo(
                f"Date range: {stats['date_range'][0]} to {stats['date_range'][1]}"
            )
        else:
            click.echo("Date range: No data")

        click.echo("\nBy Currency:")
        for currency, count in sorted(
            stats["by_currency"].items(), key=lambda x: -x[1]
        ):
            click.echo(f"  {currency}: {count}")

        click.echo("\nBy Impact:")
        for impact, count in sorted(stats["by_impact"].items(), key=lambda x: -x[1]):
            click.echo(f"  {impact}: {count}")

    except Exception as e:
        click.echo(f"Error getting stats: {e}", err=True)
        raise click.Abort()


@db.command("export")
@click.option(
    "--format",
    "-f",
    type=click.Choice(["csv", "json"]),
    default="json",
    help="Export format",
)
@click.option("--year", "-y", type=int, default=None, help="Year to export")
@click.option("--month", "-m", type=int, default=None, help="Month to export")
@click.option("--output", "-o", type=click.Path(), help="Output file (default: stdout)")
def db_export(
    format: str,
    year: int | None,
    month: int | None,
    output: str | None,
) -> None:
    """Export stored events to CSV or JSON.

    Exports all events or filter by year/month.

    Examples:
        blackbox db export --format json
        blackbox db export --format csv --year 2026 --month 1 -o events.csv
    """
    try:
        with get_session() as session:
            repo = EventRepository(session)

            # Determine date range
            if year and month:
                import calendar as cal

                _, last_day = cal.monthrange(year, month)
                start_date = date(year, month, 1)
                end_date = date(year, month, last_day)
            else:
                # Export all data
                stats = repo.get_stats()
                if not stats["date_range"][0]:
                    click.echo("No data to export.", err=True)
                    return
                start_date, end_date = stats["date_range"]

            events = repo.get_events(start_date, end_date)

            if format == "json":
                data = {
                    "exported_at": date.today().isoformat(),
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_events": len(events),
                    "events": [
                        {
                            "date": e.date.isoformat(),
                            "time": e.time.isoformat() if e.time else None,
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
                content = json.dumps(data, indent=2)
            else:  # csv
                string_buffer = StringIO()
                writer = csv.writer(string_buffer)
                writer.writerow(
                    [
                        "date",
                        "time",
                        "currency",
                        "impact",
                        "event_name",
                        "actual",
                        "forecast",
                        "previous",
                    ]
                )
                for e in events:
                    writer.writerow(
                        [
                            e.date.isoformat(),
                            e.time.isoformat() if e.time else "",
                            e.currency,
                            e.impact.value,
                            e.event_name,
                            e.actual or "",
                            e.forecast or "",
                            e.previous or "",
                        ]
                    )
                content = string_buffer.getvalue()

            if output:
                with open(output, "w") as f:
                    f.write(content)
                click.echo(f"Exported {len(events)} events to {output}")
            else:
                click.echo(content)

    except Exception as e:
        click.echo(f"Error exporting data: {e}", err=True)
        raise click.Abort()


if __name__ == "__main__":
    cli()
