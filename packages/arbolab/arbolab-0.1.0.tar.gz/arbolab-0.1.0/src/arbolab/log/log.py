"""Logging helpers for arbolab."""

from __future__ import annotations

import logging
import logging.config
from datetime import datetime

from arbolab.config import LoggingConfig
from arbolab.utils import path as pathutil
from arbolab.utils.path import PathLike

from .color import should_use_colors

# Public API surface
__all__ = ["setup_basic_logging", "setup_logging", "get_logger"]


_BASE_LOGGER_NAME = "arbolab"


def _resolved_level(level: int | str | None) -> int:
    if level is None:
        return logging.INFO
    if isinstance(level, int):
        return level
    try:
        return logging._nameToLevel[str(level).upper()]
    except KeyError:
        return logging.INFO


def _build_config(cfg: LoggingConfig, *, working_directory: PathLike | None) -> tuple[dict, bool]:
    """Return a ``dictConfig`` dictionary and whether colours are enabled."""
    level = _resolved_level(cfg.level)
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    use_colors = should_use_colors(cfg.use_colors)

    formatters: dict[str, dict] = {
        "standard": {"format": fmt, "datefmt": datefmt, "class": "logging.Formatter"}
    }
    if use_colors:
        formatters["color"] = {
            "()": "arbolab.log.color.ColorFormatter",
            "format": fmt,
            "datefmt": datefmt,
            "enable": True,
        }

    handlers: dict[str, dict] = {
        "console": {
            "class": "logging.StreamHandler",
            "level": level,
            "formatter": "color" if use_colors else "standard",
        }
    }

    wd = pathutil.WorkDir(working_directory)
    if cfg.save_to_file and wd.root is not None:
        ts = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        log_file = wd.logs / f"arbolab_{ts}.log"
        handlers["file"] = {
            "class": "logging.FileHandler",
            "level": level,
            "formatter": "standard",
            "filename": str(log_file),
            "encoding": "utf-8",
        }

    loggers = {
        _BASE_LOGGER_NAME: {
            "handlers": list(handlers.keys()),
            "level": level,
            "propagate": False,
        }
    }

    config_dict = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": formatters,
        "handlers": handlers,
        "loggers": loggers,
    }
    return config_dict, use_colors


def setup_basic_logging(level: int | str = "INFO") -> logging.Logger:
    """Configure a simple console logger using :func:`logging.basicConfig`.

    This lightweight helper is intended for standard use cases where the
    advanced features of :func:`setup_logging` are unnecessary.
    """
    resolved = _resolved_level(level)
    fmt = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    logging.basicConfig(level=resolved, format=fmt, datefmt=datefmt, force=True)
    logger = logging.getLogger(_BASE_LOGGER_NAME)
    logger.setLevel(resolved)
    return logger


def setup_logging(
    *,
    config: LoggingConfig | None = None,
    working_directory: PathLike | None = None,
) -> logging.Logger:
    """Configure project-wide logging once and return the base logger."""
    cfg = config or LoggingConfig()
    config_dict, _ = _build_config(cfg, working_directory=working_directory)
    logging.config.dictConfig(config_dict)

    if cfg.tune_matplotlib:
        logging.getLogger("matplotlib").setLevel(logging.WARNING)

    return logging.getLogger(_BASE_LOGGER_NAME)


def _normalize_name(name: str) -> str:
    if name == _BASE_LOGGER_NAME or name.startswith(_BASE_LOGGER_NAME + "."):
        return name
    return f"{_BASE_LOGGER_NAME}.{name}"


def get_logger(
    name: str | None = None,
    *,
    extra: dict[str, object] | None = None,
) -> logging.Logger | logging.LoggerAdapter:
    """Retrieve a project logger or a child logger.

    Parameters
    ----------
    name:
        Optional child name. When omitted, returns the base ``arbolab`` logger.
        When a plain module/component name is passed, it is namespaced under
        ``arbolab.<name>``.
    extra:
        Optional dict of contextual fields. When provided, a ``LoggerAdapter``
        is returned that injects these fields into log records. The default
        formatter does not render these fields, but they can be used by custom
        formatters/filters as needed.
    """
    base_name = _BASE_LOGGER_NAME if name is None else _normalize_name(name)
    logger = logging.getLogger(base_name)
    if extra:
        return logging.LoggerAdapter(logger, extra)
    return logger
