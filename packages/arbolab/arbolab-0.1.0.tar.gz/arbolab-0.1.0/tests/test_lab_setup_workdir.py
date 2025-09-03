from pathlib import Path

from arbolab.config import Config
from arbolab.lab import Lab


def test_lab_setup_creates_missing_work_dir(tmp_path: Path) -> None:
    wd = tmp_path / "missing"
    assert not wd.exists()
    cfg = Config(working_dir=wd)
    # Config should normalise and create the working directory
    assert wd.exists()
    lab = Lab.setup(cfg, load_plugins=False)
    assert lab.config.working_dir == wd
    assert wd.is_dir()
