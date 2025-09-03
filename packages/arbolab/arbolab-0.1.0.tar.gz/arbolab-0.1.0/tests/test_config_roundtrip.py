"""Tests for configuration serialization roundtrips."""

from __future__ import annotations

import importlib.util
import sys
from pathlib import Path
from types import ModuleType


def _load_config_module() -> ModuleType:
    path = Path(__file__).resolve().parents[1] / "src" / "arbolab" / "config.py"
    spec = importlib.util.spec_from_file_location("arbolab.config", path)
    if spec is None:
        raise ImportError("Could not load module specification for arbolab.config")
    module = importlib.util.module_from_spec(spec)
    assert spec.loader
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def test_from_dict_to_dict_roundtrip(tmp_path: Path) -> None:
    config = _load_config_module()
    db_file = tmp_path / f"{tmp_path.name}.duckdb"
    data = {
        "working_dir": str(tmp_path),
        "db_url": f"duckdb:///{db_file}",
        "db": {"echo": True, "engine_kwargs": {"foo": "bar"}},
        "plot": {"backend": "Agg", "style": "ggplot"},
        "logging": {
            "level": "WARNING",
            "use_colors": True,
            "save_to_file": True,
            "tune_matplotlib": True,
        },
    }

    cfg = config.Config.from_dict(data)

    assert cfg.to_dict() == data
