"""Helpers for measuring and logging runtime of code blocks.

This module currently exposes :class:`log_runtime`, a small context manager
and decorator that measures the execution time of a block of code and logs the
result.  It integrates with the project wide logging system and can be used as
follows:

>>> from arbolab.utils.runtime import log_runtime
>>> with log_runtime("load data"):
...     load_data()

The class also works as a decorator which applies the timing logic around the
decorated function.
"""

from __future__ import annotations

import logging
import time
from contextlib import ContextDecorator
from types import TracebackType

from arbolab.log import get_logger

__all__ = ["log_runtime"]


class log_runtime(ContextDecorator):
    """Measure runtime of a code block and log the elapsed time.

    Parameters
    ----------
    name:
        Label used in the log message.
    logger:
        Logger instance to emit the message to.  Defaults to the module logger
        obtained via :func:`arbolab.log.get_logger`.
    level:
        Logging level used for the message.  Defaults to ``logging.DEBUG``.
    enabled:
        When ``False`` the context manager does nothing and no message is
        emitted.
    """

    def __init__(
        self,
        name: str,
        *,
        logger: logging.Logger | logging.LoggerAdapter | None = None,
        level: int = logging.DEBUG,
        enabled: bool = True,
    ) -> None:
        self.name = name
        self.logger = logger or get_logger(__name__)
        self.level = level
        self.enabled = enabled
        self._start: float | None = None

    def __enter__(self) -> log_runtime:
        if self.enabled:
            self._start = time.perf_counter()
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> bool:
        if self.enabled and self._start is not None:
            elapsed = time.perf_counter() - self._start
            self.logger.log(self.level, "%s took %.3fs", self.name, elapsed)
        return False  # Do not suppress exceptions
