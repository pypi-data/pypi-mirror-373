from pathlib import Path

import pytest

from arbolab.classes.project import Project
from arbolab.config import Config, DBConfig, PlotConfig, LoggingConfig
from arbolab.lab import Lab


def test_lab_setup_and_load(tmp_path: Path) -> None:
    cfg = Config(
        working_dir=tmp_path,
        logging=LoggingConfig(level="DEBUG"),
        db=DBConfig(echo=True),
        plot=PlotConfig(backend="Agg"),
    )
    lab = Lab.setup(cfg, load_plugins=False)
    Project.setup(lab, "demo")
    db_file = Path(lab.config.db_url.split("///", 1)[1])

    loaded = Lab.load(db_file, load_plugins=False)
    persisted = loaded.config_store.load()
    assert persisted == loaded.config
    assert loaded.config.log_level == "DEBUG"
    assert loaded.config.db.echo is True
    assert loaded.config.plot.backend == "Agg"
    project = Project.load(loaded, "demo")
    assert project.name == "demo"


def test_lab_load_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.duckdb"
    with pytest.raises(FileNotFoundError):
        Lab.load(missing, load_plugins=False)
