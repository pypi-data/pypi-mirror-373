"""Colour utilities for logging.

This module hosts the colour aware formatter as well as a small helper to
decide whether colours should be used at all.  Keeping this functionality in a
separate module avoids importing it when colour output is not desired.
"""

from __future__ import annotations

import copy
import logging
import sys

__all__ = ["ColorFormatter", "should_use_colors"]


class ColorFormatter(logging.Formatter):
    """Minimal colourising formatter using ANSI escape codes."""

    COLORS = {
        logging.CRITICAL: "\x1b[91m",  # bright red
        logging.ERROR: "\x1b[91m",  # bright red
        logging.WARNING: "\x1b[93m",  # bright yellow
        logging.INFO: "\x1b[92m",  # bright green
        logging.DEBUG: "\x1b[94m",  # bright blue
    }
    RESET = "\x1b[0m"

    def __init__(self, fmt: str, datefmt: str | None = None, *, enable: bool) -> None:
        super().__init__(fmt=fmt, datefmt=datefmt)
        self._enable = enable

    def format(self, record: logging.LogRecord) -> str:  # pragma: no cover - thin wrapper
        """Format a log record, colorizing the level name when enabled.

        Parameters
        ----------
        record : logging.LogRecord
            The log record to format.

        Returns
        -------
        str
            The formatted log message.
        """
        if not self._enable:
            return super().format(record)
        colored = copy.copy(record)
        color = self.COLORS.get(record.levelno, self.RESET)
        colored.levelname = f"{color}{record.levelname}{self.RESET}"
        return super().format(colored)


def should_use_colors(flag: bool | None) -> bool:
    """Return ``True`` when coloured output should be enabled."""
    if flag is not None:
        return flag
    try:
        return sys.stderr.isatty() or sys.stdout.isatty()
    except OSError:
        logging.getLogger(__name__).exception("Failed to determine if output is a TTY")
        return False
