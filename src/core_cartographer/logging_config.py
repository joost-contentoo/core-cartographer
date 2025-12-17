"""Logging configuration for Core Cartographer.

This module provides a centralized logging setup that can be used
throughout the application. It supports both file and console logging.
"""

import logging
import sys
from pathlib import Path

# Default format for log messages
DEFAULT_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
SIMPLE_FORMAT = "%(levelname)s: %(message)s"


def setup_logging(
    level: int = logging.INFO,
    log_file: Path | None = None,
    console: bool = True,
    format_string: str = DEFAULT_FORMAT,
) -> logging.Logger:
    """
    Configure logging for the application.

    Args:
        level: The logging level (e.g., logging.DEBUG, logging.INFO).
        log_file: Optional path to write logs to a file.
        console: Whether to output logs to console.
        format_string: The format string for log messages.

    Returns:
        The configured root logger for the application.
    """
    # Get the root logger for our package
    logger = logging.getLogger("core_cartographer")
    logger.setLevel(level)

    # Remove any existing handlers to avoid duplicates
    logger.handlers.clear()

    formatter = logging.Formatter(format_string)

    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setLevel(level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        name: The module name (typically __name__).

    Returns:
        A logger instance for the module.

    Example:
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing document")
    """
    return logging.getLogger(f"core_cartographer.{name}")


# Convenience function to set log level at runtime
def set_log_level(level: int) -> None:
    """
    Change the logging level at runtime.

    Args:
        level: The new logging level.
    """
    logger = logging.getLogger("core_cartographer")
    logger.setLevel(level)
    for handler in logger.handlers:
        handler.setLevel(level)
