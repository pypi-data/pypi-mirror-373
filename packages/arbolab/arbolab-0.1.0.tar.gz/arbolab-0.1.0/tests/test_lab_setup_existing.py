import logging
from pathlib import Path

from arbolab import Config, setup
from arbolab.classes.project import Project


def test_lab_setup_warns_and_loads_existing(tmp_path: Path, caplog) -> None:
    config = Config(working_dir=tmp_path)
    lab1 = setup(config=config, load_plugins=False)
    Project.setup(lab1, "demo")

    caplog.clear()
    with caplog.at_level(logging.WARNING):
        lab2 = setup(config=config, load_plugins=False)

    assert any("already exists" in rec.message for rec in caplog.records)
    assert Project.load(lab2, "demo").name == "demo"
