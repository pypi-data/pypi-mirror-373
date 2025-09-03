"""
Company: eXonware.com
Author: Eng. Muhammad AlShehri
Email: connect@exonware.com
Version: 0.0.1
Generation Date: August 31, 2025

Logging configuration for xSystem.

Provides simple logging control functions and configuration management.
"""

import logging
import os
from typing import Union

from .defaults import LOGGING_ENABLED, LOGGING_LEVEL


class LoggingConfig:
    """Simple logging configuration control."""

    def __init__(self) -> None:
        self._enabled: bool = LOGGING_ENABLED
        self._level: str = LOGGING_LEVEL

    def disable(self) -> None:
        """Disable all logging."""
        # Disable logging BEFORE any other imports
        os.environ["XSYSTEM_LOGGING_DISABLE"] = "true"
        logging.disable(logging.CRITICAL)
        self._enabled = False

    def enable(self) -> None:
        """Enable logging."""
        self._enabled = True
        os.environ["XSYSTEM_LOGGING_DISABLE"] = "false"
        logging.disable(logging.NOTSET)

    def set_level(self, level: str) -> None:
        """Set logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)."""
        self._level = level.upper()
        if self._enabled:
            logging.getLogger().setLevel(getattr(logging, self._level))

    @property
    def enabled(self) -> bool:
        """Check if logging is enabled."""
        return self._enabled

    @property
    def level(self) -> str:
        """Get current logging level."""
        return self._level


# Global logging config instance
logging_config = LoggingConfig()


# Convenience functions
def logging_disable() -> None:
    """Disable all logging."""
    os.environ["XSYSTEM_LOGGING_DISABLE"] = "true"
    logging.disable(logging.CRITICAL)


def logging_enable() -> None:
    """Enable logging."""
    logging_config.enable()


def logging_set_level(level: str) -> None:
    """Set logging level."""
    logging_config.set_level(level)
