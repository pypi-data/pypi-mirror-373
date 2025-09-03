from pathlib import Path

import pytest

from arbolab.utils.path import WorkDir, ensure_dir


def test_workdir_creates_subdirectories(tmp_path: Path) -> None:
    wd = WorkDir(tmp_path)
    assert wd.logs.is_dir()
    assert wd.plots.is_dir()
    assert wd.data.is_dir()
    assert wd.db.is_dir()
    db_file = wd.db_path()
    assert db_file.parent == wd.db


def test_workdir_raises_without_root() -> None:
    wd = WorkDir(None)
    with pytest.raises(ValueError):
        _ = wd.logs


def test_ensure_dir_none_raises_typeerror() -> None:
    with pytest.raises(TypeError):
        ensure_dir(None)
