"""Tests for configuration loading utilities."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml
from pytest import MonkeyPatch

from arbolab.config import Config, LoggingConfig


def test_from_env(monkeypatch: MonkeyPatch, tmp_path: Path) -> None:
    monkeypatch.setenv("ARBOLAB_WORKING_DIR", str(tmp_path))
    monkeypatch.setenv("ARBOLAB_DB_URL", "duckdb:///example.duckdb")
    monkeypatch.setenv("ARBOLAB_LOGGING__LEVEL", "WARNING")
    monkeypatch.setenv("ARBOLAB_LOGGING__USE_COLORS", "true")
    monkeypatch.setenv("ARBOLAB_LOGGING__SAVE_TO_FILE", "false")
    monkeypatch.setenv("ARBOLAB_LOGGING__TUNE_MATPLOTLIB", "1")

    cfg = Config.from_env()

    assert cfg.working_dir == tmp_path
    assert cfg.db_url == "duckdb:///example.duckdb"
    assert cfg.log_level == "WARNING"
    assert cfg.logging.use_colors is True
    assert cfg.logging.save_to_file is False
    assert cfg.logging.tune_matplotlib is True


def test_from_file(tmp_path: Path) -> None:
    data = {
        "working_dir": str(tmp_path),
        "db_url": "duckdb:///file.duckdb",
        "logging": {"use_colors": False, "level": "INFO"},
    }
    cfg_path = tmp_path / "config.yml"
    cfg_path.write_text(yaml.safe_dump(data), encoding="utf-8")

    cfg = Config.from_file(cfg_path)

    assert cfg.working_dir == tmp_path
    assert cfg.db_url == "duckdb:///file.duckdb"
    assert cfg.log_level == "INFO"
    assert cfg.logging.level == "INFO"
    assert cfg.logging.use_colors is False


def test_from_file_missing(tmp_path: Path) -> None:
    cfg_path = tmp_path / "missing.yml"
    with pytest.raises(FileNotFoundError, match="Config file not found"):
        Config.from_file(cfg_path)


def test_from_file_invalid_yaml(tmp_path: Path) -> None:
    cfg_path = tmp_path / "bad.yml"
    cfg_path.write_text("::this is: [not yaml", encoding="utf-8")
    with pytest.raises(ValueError, match="Invalid YAML"):
        Config.from_file(cfg_path)


@pytest.mark.parametrize(
    "data",
    [
        {"logging": {"level": "DEBUG"}},
        {"logging": {"log_level": "DEBUG"}},
    ],
)
def test_from_dict_normalises_log_level(data: dict[str, object]) -> None:
    cfg = Config.from_dict(data)
    assert cfg.log_level == "DEBUG"
    assert cfg.logging.level == "DEBUG"


def test_constructor_normalises_log_level() -> None:
    cfg = Config(logging=LoggingConfig(level="info"))
    assert cfg.log_level == "INFO"
    assert cfg.logging.level == "INFO"
