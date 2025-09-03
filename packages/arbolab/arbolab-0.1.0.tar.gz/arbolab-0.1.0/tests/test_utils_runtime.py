import logging
import time
from pathlib import Path

from arbolab.log import get_logger, setup_logging
from arbolab.config import LoggingConfig
from arbolab.utils.runtime import log_runtime


class ListHandler(logging.Handler):
    def __init__(self) -> None:
        super().__init__()
        self.records: list[logging.LogRecord] = []

    def emit(self, record: logging.LogRecord) -> None:  # pragma: no cover - trivial
        self.records.append(record)


def _cleanup_logging() -> None:
    base = get_logger()
    for h in base.handlers:
        h.close()
    base.handlers.clear()


def test_log_runtime_logs_elapsed(tmp_path: Path) -> None:
    setup_logging(
        config=LoggingConfig(level="DEBUG", use_colors=False), working_directory=tmp_path
    )
    logger = get_logger("runtime")
    handler = ListHandler()
    logger.addHandler(handler)

    with log_runtime("sleep", logger=logger):
        time.sleep(0.01)

    messages = [rec.getMessage() for rec in handler.records]
    assert any(msg.startswith("sleep took") for msg in messages)

    logger.removeHandler(handler)
    _cleanup_logging()

def test_log_runtime_can_be_disabled(tmp_path: Path) -> None:
    setup_logging(
        config=LoggingConfig(level="DEBUG", use_colors=False), working_directory=tmp_path
    )
    logger = get_logger("runtime")
    handler = ListHandler()
    logger.addHandler(handler)

    with log_runtime("sleep", logger=logger, enabled=False):
        time.sleep(0.01)

    messages = [rec.getMessage() for rec in handler.records]
    assert not any(msg.startswith("sleep took") for msg in messages)

    logger.removeHandler(handler)
    _cleanup_logging()
