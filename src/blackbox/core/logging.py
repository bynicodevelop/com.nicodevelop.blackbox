"""Logging configuration for Blackbox Trading Robot.

This module provides a centralized logging system with:
- Console output with colors
- Daily rotating log files
- Configurable log levels
"""

import logging
import sys
from datetime import datetime
from logging.handlers import TimedRotatingFileHandler
from pathlib import Path


# ANSI color codes for terminal output
class LogColors:
    """ANSI color codes for log levels."""

    RESET = "\033[0m"
    DEBUG = "\033[36m"  # Cyan
    INFO = "\033[32m"  # Green
    WARNING = "\033[33m"  # Yellow
    ERROR = "\033[31m"  # Red
    CRITICAL = "\033[35m"  # Magenta
    TIMESTAMP = "\033[90m"  # Gray
    NAME = "\033[34m"  # Blue


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output."""

    COLORS = {
        logging.DEBUG: LogColors.DEBUG,
        logging.INFO: LogColors.INFO,
        logging.WARNING: LogColors.WARNING,
        logging.ERROR: LogColors.ERROR,
        logging.CRITICAL: LogColors.CRITICAL,
    }

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with colors."""
        color = self.COLORS.get(record.levelno, LogColors.RESET)

        # Format timestamp
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")

        # Format level name with fixed width
        levelname = f"{record.levelname:<8}"

        # Format message
        message = record.getMessage()

        # Build colored output
        output = (
            f"{LogColors.TIMESTAMP}{timestamp}{LogColors.RESET} "
            f"{color}{levelname}{LogColors.RESET} "
            f"{LogColors.NAME}[{record.name}]{LogColors.RESET} "
            f"{message}"
        )

        # Add exception info if present
        if record.exc_info:
            output += f"\n{self.formatException(record.exc_info)}"

        return output


class FileFormatter(logging.Formatter):
    """Standard formatter for file output."""

    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


# Global configuration
_log_dir: Path | None = None
_initialized: bool = False
_console_level: int = logging.INFO
_file_level: int = logging.DEBUG


def get_log_directory() -> Path:
    """Get or create the log directory.

    Returns:
        Path to the logs directory.
    """
    global _log_dir

    if _log_dir is None:
        # Default to project root / logs
        _log_dir = Path.cwd() / "logs"

    _log_dir.mkdir(parents=True, exist_ok=True)
    return _log_dir


def set_log_directory(path: Path | str) -> None:
    """Set custom log directory.

    Args:
        path: Path to the log directory.
    """
    global _log_dir
    _log_dir = Path(path)
    _log_dir.mkdir(parents=True, exist_ok=True)


def setup_logging(
    console_level: int = logging.INFO,
    file_level: int = logging.DEBUG,
    log_dir: Path | str | None = None,
) -> None:
    """Initialize the logging system.

    Args:
        console_level: Log level for console output.
        file_level: Log level for file output.
        log_dir: Optional custom log directory.
    """
    global _initialized, _console_level, _file_level

    if _initialized:
        return

    _console_level = console_level
    _file_level = file_level

    if log_dir:
        set_log_directory(log_dir)

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)  # Capture all, handlers will filter

    # Remove existing handlers
    root_logger.handlers.clear()

    # Console handler with colors
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(console_level)
    console_handler.setFormatter(ColoredFormatter())
    root_logger.addHandler(console_handler)

    # File handler with daily rotation
    log_file = get_log_directory() / "blackbox.log"
    file_handler = TimedRotatingFileHandler(
        filename=log_file,
        when="midnight",
        interval=1,
        backupCount=30,  # Keep 30 days of logs
        encoding="utf-8",
    )
    file_handler.setLevel(file_level)
    file_handler.setFormatter(FileFormatter())
    file_handler.suffix = "%Y-%m-%d"  # Add date to rotated files
    root_logger.addHandler(file_handler)

    _initialized = True

    # Log initialization
    logger = logging.getLogger("blackbox.logging")
    logger.debug(
        f"Logging initialized - Console: {logging.getLevelName(console_level)}, File: {logging.getLevelName(file_level)}"
    )
    logger.debug(f"Log directory: {get_log_directory()}")


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name.

    Automatically initializes logging if not already done.

    Args:
        name: Logger name (typically module name).

    Returns:
        Configured logger instance.
    """
    if not _initialized:
        setup_logging()

    return logging.getLogger(name)


def set_console_level(level: int) -> None:
    """Change console log level at runtime.

    Args:
        level: New log level (e.g., logging.DEBUG).
    """
    for handler in logging.getLogger().handlers:
        if isinstance(handler, logging.StreamHandler) and not isinstance(
            handler, TimedRotatingFileHandler
        ):
            handler.setLevel(level)


def set_file_level(level: int) -> None:
    """Change file log level at runtime.

    Args:
        level: New log level (e.g., logging.DEBUG).
    """
    for handler in logging.getLogger().handlers:
        if isinstance(handler, TimedRotatingFileHandler):
            handler.setLevel(level)
