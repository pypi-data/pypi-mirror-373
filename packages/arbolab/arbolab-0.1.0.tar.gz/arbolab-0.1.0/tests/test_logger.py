import logging
import logging.config
from pathlib import Path

import pytest

from arbolab.log.color import ColorFormatter
from arbolab.log import get_logger, setup_basic_logging, setup_logging
from arbolab.config import LoggingConfig


def test_setup_logging_resets_handlers_and_creates_file(tmp_path: Path) -> None:
    cfg = LoggingConfig(level="INFO", save_to_file=False, use_colors=False)
    logger = setup_logging(config=cfg, working_directory=tmp_path)
    assert logger.name == "arbolab"
    assert logger.level == logging.INFO
    assert len(logger.handlers) == 1
    handler = logger.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    assert isinstance(handler.formatter, logging.Formatter)
    assert not isinstance(handler.formatter, ColorFormatter)

    cfg2 = LoggingConfig(level="DEBUG", save_to_file=True, use_colors=False)
    logger = setup_logging(config=cfg2, working_directory=tmp_path)
    assert logger.level == logging.DEBUG
    assert len(logger.handlers) == 2
    assert any(isinstance(h, logging.FileHandler) for h in logger.handlers)
    log_files = list((tmp_path / "logs").glob("arbolab_*.log"))
    assert len(log_files) == 1

    for h in logger.handlers:
        h.close()
    logger.handlers.clear()


def test_setup_logging_use_colors(tmp_path: Path) -> None:
    cfg = LoggingConfig(use_colors=True)
    logger = setup_logging(config=cfg, working_directory=tmp_path)
    handler = logger.handlers[0]
    assert isinstance(handler.formatter, ColorFormatter)
    assert handler.formatter._enable is True

    for h in logger.handlers:
        h.close()
    logger.handlers.clear()


def test_setup_logging_passes_dictconfig(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    captured: dict = {}

    def fake_dict_config(cfg: dict) -> None:
        captured.update(cfg)

    monkeypatch.setattr(logging.config, "dictConfig", fake_dict_config)

    setup_logging(config=LoggingConfig(use_colors=False), working_directory=tmp_path)

    assert "handlers" in captured
    assert "console" in captured["handlers"]
    assert captured["loggers"]["arbolab"]["handlers"] == ["console"]


def test_setup_basic_logging_configures_root() -> None:
    logger = setup_basic_logging(level="DEBUG")
    assert logger.name == "arbolab"
    assert logger.level == logging.DEBUG
    root = logging.getLogger()
    assert len(root.handlers) == 1
    handler = root.handlers[0]
    assert isinstance(handler, logging.StreamHandler)
    for h in root.handlers:
        h.close()
    root.handlers.clear()


def test_get_logger_namespacing_and_adapter(tmp_path: Path) -> None:
    setup_logging(config=LoggingConfig(use_colors=False), working_directory=tmp_path)
    base = get_logger()
    assert base.name == "arbolab"

    child = get_logger("child")
    assert child.name == "arbolab.child"

    prefixed = get_logger("arbolab.special")
    assert prefixed.name == "arbolab.special"

    adapter = get_logger("extra", extra={"foo": "bar"})
    assert isinstance(adapter, logging.LoggerAdapter)
    assert adapter.logger.name == "arbolab.extra"
    assert adapter.extra == {"foo": "bar"}

    for h in base.handlers:
        h.close()
    base.handlers.clear()


def test_color_formatter_does_not_mutate_record() -> None:
    formatter = ColorFormatter("%(levelname)s: %(message)s", enable=True)
    record = logging.LogRecord("test", logging.INFO, "", 0, "msg", args=(), exc_info=None)
    original = record.levelname
    formatter.format(record)
    assert record.levelname == original
