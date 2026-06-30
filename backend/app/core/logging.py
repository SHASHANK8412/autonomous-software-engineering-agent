"""Application logging configuration utilities.

This module centralizes logging setup so all backend components use the same
format, level, and root logger behavior.
"""

from __future__ import annotations

import logging
from logging.config import dictConfig


LOG_FORMAT = "%(asctime)s | %(levelname)s | %(name)s | %(message)s"


def configure_logging(level: int = logging.INFO) -> None:
    """Configure the application-wide logging pipeline.

    Parameters
    ----------
    level:
        The default severity threshold for the root logger.
    """

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "standard": {
                    "format": LOG_FORMAT,
                }
            },
            "handlers": {
                "console": {
                    "class": "logging.StreamHandler",
                    "formatter": "standard",
                }
            },
            "root": {
                "handlers": ["console"],
                "level": level,
            },
        }
    )


def get_logger(name: str) -> logging.Logger:
    """Return a namespaced logger for the given module name."""

    return logging.getLogger(name)