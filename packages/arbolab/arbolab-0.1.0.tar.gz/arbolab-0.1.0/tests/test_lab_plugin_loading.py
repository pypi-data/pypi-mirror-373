"""Tests for plugin loading during Lab setup and load."""

from pathlib import Path

import pytest

import arbolab.lab as lab_module
from arbolab.config import Config
from arbolab.lab import Lab
from arbolab.plugin_manager import PluginManager


def test_setup_calls_load_plugins(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[Lab] = []

    def fake_load(
        self: lab_module.PluginManager,
        core: Lab,
        *,
        group: str = "arbolab.adapters",
    ) -> None:
        calls.append(core)

    monkeypatch.setattr(lab_module.PluginManager, "load", fake_load)

    lab = Lab.setup(Config(working_dir=tmp_path), load_plugins=True)

    assert calls == [lab]


def test_setup_skips_plugin_loading(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[Lab] = []

    def fake_load(
        self: lab_module.PluginManager,
        core: Lab,
        *,
        group: str = "arbolab.adapters",
    ) -> None:
        calls.append(core)

    monkeypatch.setattr(lab_module.PluginManager, "load", fake_load)

    Lab.setup(Config(working_dir=tmp_path), load_plugins=False)

    assert calls == []


def test_load_calls_load_plugins(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[Lab] = []

    def fake_load(
        self: lab_module.PluginManager,
        core: Lab,
        *,
        group: str = "arbolab.adapters",
    ) -> None:
        calls.append(core)

    monkeypatch.setattr(lab_module.PluginManager, "load", fake_load)

    Lab.setup(Config(working_dir=tmp_path), load_plugins=False)
    db_file = tmp_path / f"{tmp_path.name}.duckdb"
    loaded = Lab.load(db_file, load_plugins=True)

    assert calls == [loaded]


def test_load_skips_plugin_loading(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    calls: list[Lab] = []

    def fake_load(
        self: lab_module.PluginManager,
        core: Lab,
        *,
        group: str = "arbolab.adapters",
    ) -> None:
        calls.append(core)

    monkeypatch.setattr(lab_module.PluginManager, "load", fake_load)

    Lab.setup(Config(working_dir=tmp_path), load_plugins=False)
    Lab.load(tmp_path / f"{tmp_path.name}.duckdb", load_plugins=False)

    assert calls == []


def test_setup_accepts_custom_plugin_manager(tmp_path: Path) -> None:
    class CustomPluginManager(PluginManager):
        pass

    pm = CustomPluginManager()
    lab = Lab.setup(Config(working_dir=tmp_path), load_plugins=False, plugin_manager=pm)

    assert lab.plugins is pm


def test_load_accepts_custom_plugin_manager(tmp_path: Path) -> None:
    class CustomPluginManager(PluginManager):
        pass

    pm = CustomPluginManager()
    Lab.setup(Config(working_dir=tmp_path), load_plugins=False)
    db_file = tmp_path / f"{tmp_path.name}.duckdb"

    lab = Lab.load(db_file, load_plugins=False, plugin_manager=pm)

    assert lab.plugins is pm
