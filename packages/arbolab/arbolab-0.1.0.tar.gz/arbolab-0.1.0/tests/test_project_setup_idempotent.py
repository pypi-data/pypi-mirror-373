from pathlib import Path

import logging

from arbolab import Config, setup
from arbolab.classes.project import Project


def test_project_setup_is_idempotent(tmp_path: Path, caplog) -> None:
    config = Config(working_dir=tmp_path)
    lab = setup(config=config, load_plugins=False)
    first = Project.setup(lab, "demo")
    caplog.clear()
    with caplog.at_level(logging.WARNING):
        second = Project.setup(lab, "demo")
    assert first.id == second.id
    assert any("already exists" in rec.message for rec in caplog.records)
