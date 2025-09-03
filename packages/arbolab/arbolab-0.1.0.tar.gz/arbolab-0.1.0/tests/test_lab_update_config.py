import json
import logging
from pathlib import Path

from sqlalchemy import select

from arbolab.classes.base_config import Config as ConfigEntry
from arbolab.config import Config, LoggingConfig, PlotConfig
from arbolab.lab import Lab
from arbolab.plotting import Plotter


def test_update_log_level_persists(tmp_path: Path) -> None:
    cfg = Config(working_dir=tmp_path, logging=LoggingConfig(level="INFO"))
    lab = Lab.setup(cfg, load_plugins=False)

    assert lab.logger.level == logging.INFO

    lab.update_config(log_level="DEBUG")

    assert lab.config.log_level == "DEBUG"
    assert lab.logger.level == logging.DEBUG

    with lab.db.session() as sess:
        row = sess.scalar(select(ConfigEntry).where(ConfigEntry.key == "config"))
        assert json.loads(row.value)["logging"]["level"] == "DEBUG"


def test_update_log_level_none(tmp_path: Path) -> None:
    cfg = Config(working_dir=tmp_path, logging=LoggingConfig(level="INFO"))
    lab = Lab.setup(cfg, load_plugins=False)

    lab.update_config(log_level=None)

    assert lab.config.log_level == "INFO"
    assert lab.logger.level == logging.INFO
    with lab.db.session() as sess:
        row = sess.scalar(select(ConfigEntry).where(ConfigEntry.key == "config"))
        assert json.loads(row.value)["logging"]["level"] == "INFO"


def test_update_db_url(tmp_path: Path) -> None:
    cfg = Config(working_dir=tmp_path, logging=LoggingConfig(level="INFO"))
    lab = Lab.setup(cfg, load_plugins=False)

    new_db = tmp_path / "new.duckdb"
    lab.update_config(db_url=f"duckdb:///{new_db}")

    assert Path(lab.config.db_url.split("///", 1)[1]) == new_db

    with lab.db.session() as sess:
        row = sess.scalar(select(ConfigEntry).where(ConfigEntry.key == "config"))
        assert json.loads(row.value)["logging"]["level"] == lab.config.log_level


def test_reconfigure_logging_level_only(tmp_path: Path) -> None:
    cfg = Config(working_dir=tmp_path, logging=LoggingConfig(level="INFO"))
    lab = Lab.setup(cfg, load_plugins=False)

    old_logger = lab.logger
    lab.config.log_level = "DEBUG"
    lab._reconfigure_logging(log_changed=True, logging_changed=False)

    assert lab.logger is old_logger
    assert lab.logger.level == logging.DEBUG
    assert all(h.level == logging.DEBUG for h in lab.logger.handlers)


def test_reconfigure_logging_level_none(tmp_path: Path) -> None:
    cfg = Config(working_dir=tmp_path, logging=LoggingConfig(level="INFO"))
    lab = Lab.setup(cfg, load_plugins=False)

    object.__setattr__(lab.config.logging, "level", None)
    lab._reconfigure_logging(log_changed=True, logging_changed=False)

    assert lab.logger.level == logging.INFO
    assert all(h.level == logging.INFO for h in lab.logger.handlers)


def test_reconfigure_logging_disable(tmp_path: Path) -> None:
    cfg = Config(working_dir=tmp_path, logging=LoggingConfig(level="INFO"))
    lab = Lab.setup(cfg, load_plugins=False)

    lab.config.log_level = "NONE"
    lab._reconfigure_logging(log_changed=True, logging_changed=False)

    assert logging.getLogger().manager.disable >= logging.CRITICAL

    lab.config.log_level = "INFO"
    lab._reconfigure_logging(log_changed=True, logging_changed=False)

    assert logging.getLogger().manager.disable == 0


def test_reconfigure_logging_refresh(tmp_path: Path) -> None:
    cfg = Config(working_dir=tmp_path, logging=LoggingConfig(level="INFO"))
    lab = Lab.setup(cfg, load_plugins=False)

    lab.config.logging = LoggingConfig(level="WARNING")
    lab.config.log_level = "WARNING"
    lab._reconfigure_logging(log_changed=False, logging_changed=True)

    assert lab.logger.level == logging.WARNING


def test_reconfigure_db(tmp_path: Path) -> None:
    cfg = Config(working_dir=tmp_path, logging=LoggingConfig(level="INFO"))
    lab = Lab.setup(cfg, load_plugins=False)

    old_db = lab.db
    new_db = tmp_path / "other.duckdb"
    lab.config.db_url = f"duckdb:///{new_db}"
    lab._reconfigure_db(True)

    assert lab.db is not old_db
    assert Path(lab.db.url.split("///", 1)[1]) == new_db


def test_reconfigure_plot(tmp_path: Path) -> None:
    cfg = Config(working_dir=tmp_path, logging=LoggingConfig(level="INFO"))
    lab = Lab.setup(cfg, load_plugins=False)

    old_plotter = lab.plotter
    lab._reconfigure_plot(True)

    assert isinstance(lab.plotter, Plotter)
    assert lab.plotter is not old_plotter


def test_persist_config(tmp_path: Path) -> None:
    cfg = Config(working_dir=tmp_path, logging=LoggingConfig(level="INFO"))
    lab = Lab.setup(cfg, load_plugins=False)

    lab.config.db.echo = True
    lab._persist_config()

    with lab.db.session() as sess:
        row = sess.scalar(select(ConfigEntry).where(ConfigEntry.key == "config"))
        assert json.loads(row.value)["db"]["echo"] is True


def test_update_config_multiple(tmp_path: Path) -> None:
    cfg = Config(working_dir=tmp_path, logging=LoggingConfig(level="INFO"))
    lab = Lab.setup(cfg, load_plugins=False)

    new_db = tmp_path / "multi.duckdb"
    lab.update_config(
        log_level="DEBUG",
        db_url=f"duckdb:///{new_db}",
        plot=PlotConfig(),
        logging=LoggingConfig(level="DEBUG"),
    )

    assert lab.logger.level == logging.DEBUG
    assert Path(lab.db.url.split("///", 1)[1]) == new_db
    assert isinstance(lab.plotter, Plotter)
    with lab.db.session() as sess:
        row = sess.scalar(select(ConfigEntry).where(ConfigEntry.key == "config"))
        assert json.loads(row.value)["logging"]["level"] == "DEBUG"
