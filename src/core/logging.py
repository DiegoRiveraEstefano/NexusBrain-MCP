"""
Logging system configuration using Structlog.
Ensures logs are structured and formatted properly.
"""

import logging
import sys

import structlog

from src.core.settings import settings


def setup_logging() -> None:
    """
    Initializes structlog.
    Uses friendly console rendering in development and JSON in production.
    """
    # Configure the standard Python logger
    logging.basicConfig(
        format="%(message)s",
        level=settings.log_level.upper(),
    )

    # Processors shared between development and production
    shared_processors = [
        structlog.stdlib.add_log_level,
        structlog.stdlib.add_logger_name,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
    ]

    # Choose the final renderer based on the environment
    if settings.environment.lower() == "production":
        renderer = structlog.processors.JSONRenderer()
    else:
        # In development, print with colors in the terminal
        renderer = structlog.dev.ConsoleRenderer(colors=True)

    structlog.configure(
        processors=shared_processors + [renderer],  # type: ignore
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.BoundLogger:
    """
    Gets a structured logger for a specific module.

    Args:
        name (str): Module name (usually __name__).

    Returns:
        structlog.BoundLogger: Configured logger instance.
    """
    return structlog.get_logger(name)
