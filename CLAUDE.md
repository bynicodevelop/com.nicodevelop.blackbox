# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Blackbox is a Python-based algorithmic trading robot with economic calendar scraping capabilities. It provides both a CLI interface (Click) and a REST API (FastAPI).

## Development Commands

All commands use the Makefile:

```bash
# Install development environment (includes pre-commit hooks)
make install-dev

# Run tests with coverage
make test

# Run tests quickly without coverage
make test-fast

# Lint and format check
make lint

# Auto-format code
make format

# Start API server (port 8000)
make run-api

# Run CLI
make run-cli

# Serve documentation (port 8001)
make docs
```

Run a single test file:
```bash
pytest tests/api/test_api.py -v
```

Run a specific test:
```bash
pytest tests/api/test_api.py::test_health_endpoint -v
```

## Architecture

```
src/blackbox/
├── api/          # FastAPI REST API (main.py entry point)
├── cli/          # Click CLI interface (main.py entry point)
├── core/         # Trading business logic (strategies, signals, portfolio)
└── data/         # Data fetching & web scraping
    ├── models.py      # Pydantic models (EconomicEvent, CalendarDay, etc.)
    ├── config.py      # Scraper configuration classes
    ├── exceptions.py  # Exception hierarchy for scraper errors
    └── scraper/       # Web scraping infrastructure
```

**Entry Points:**
- CLI: `blackbox.cli.main:cli` (installed as `blackbox` command)
- API: `blackbox.api.main:app` (FastAPI application)

**Data Flow:**
1. Scrapers fetch economic calendar data (ForexFactory)
2. Data parsed into Pydantic models with filtering capabilities
3. Core module processes signals for trading strategies
4. Results exposed via CLI commands or API endpoints

## Code Quality

- **Linter/Formatter**: ruff (line length 88, Python 3.11 target)
- **Pre-commit hooks**: ruff, bandit (security), standard file checks
- **Test framework**: pytest with coverage reporting to `htmlcov/`

The project uses double quotes and Unix line endings.

## Key Patterns

- Exception hierarchy in `data/exceptions.py` for structured error handling
- Configuration classes in `data/config.py` support user agent rotation and rate limiting
- Pydantic models with filtering methods (e.g., `CalendarDay.filter_by_impact()`)
- API has CORS enabled for all origins (development setting)
