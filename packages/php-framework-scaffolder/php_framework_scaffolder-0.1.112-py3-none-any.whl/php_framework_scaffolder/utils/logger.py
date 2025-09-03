"""Structured logging configuration using structlog."""
from __future__ import annotations

import logging
import sys

import structlog


def configure_structlog() -> None:
    """Configure structlog with consistent formatting and output."""
    # Configure structlog
    structlog.configure(
        processors=[
            # Add log level to log entries
            structlog.stdlib.add_log_level,
            # Add logger name to log entries
            structlog.stdlib.add_logger_name,
            # Add timestamp
            structlog.processors.TimeStamper(fmt='ISO'),
            # Stack info processor for exceptions
            structlog.processors.StackInfoRenderer(),
            # Exception processor for better exception formatting
            structlog.dev.set_exc_info,
            # JSONLogRenderer for structured output, or use ConsoleRenderer for development
            structlog.dev.ConsoleRenderer(colors=True) if sys.stderr.isatty(
            ) else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.stdlib.BoundLogger,
        logger_factory=structlog.stdlib.LoggerFactory(),
        context_class=dict,
        cache_logger_on_first_use=True,
    )

    # Configure standard library logging
    logging.basicConfig(
        format='%(message)s',
        stream=sys.stderr,
        level=logging.INFO,
    )


def get_logger(name: str) -> structlog.stdlib.BoundLogger:
    """Get a structured logger instance.

    Args:
        name: Logger name, typically __name__ or module name

    Returns:
        A configured structlog logger instance
    """
    return structlog.get_logger(name)


# Initialize structlog configuration
configure_structlog()
