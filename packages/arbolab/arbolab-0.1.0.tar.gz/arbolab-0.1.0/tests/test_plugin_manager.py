import logging

import pytest

from arbolab.plugin_manager import PluginManager


class DummyEntryPoint:
    """Minimal stand-in for ``importlib.metadata.EntryPoint``."""

    def __init__(self, obj: object, *, name: str | None = None) -> None:
        self._obj = obj
        self.name = name or obj.__name__
        self.value = f"{obj.__module__}:{obj.__name__}"

    def load(self) -> object:
        return self._obj


class DummyCore:
    logger = logging.getLogger("test")


def test_load_skips_faulty_plugins(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    class Good:
        name = "good"

        def attach(self, core: DummyCore) -> None:
            pass

    class Bad:
        name = "bad"

        def __init__(self) -> None:
            raise RuntimeError("boom")

        def attach(self, core: DummyCore) -> None:  # pragma: no cover - never called
            pass

    eps = [DummyEntryPoint(Good), DummyEntryPoint(Bad)]

    def fake_entry_points(group: str) -> list[DummyEntryPoint]:
        return eps if group == "arbolab.adapters" else []

    monkeypatch.setattr("arbolab.plugin_manager.entry_points", fake_entry_points)

    pm = PluginManager()
    with caplog.at_level(logging.ERROR):
        pm.load(DummyCore())

    assert list(pm.sensors) == ["good"]
    assert any("Failed to load adapter" in r.message for r in caplog.records)


def test_load_warns_on_duplicate(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    class First:
        name = "dup"

        def attach(self, core: DummyCore) -> None:
            pass

    class Second:
        name = "dup"

        def attach(self, core: DummyCore) -> None:
            pass

    eps = [DummyEntryPoint(First), DummyEntryPoint(Second)]

    def fake_entry_points(group: str) -> list[DummyEntryPoint]:
        return eps if group == "arbolab.adapters" else []

    monkeypatch.setattr("arbolab.plugin_manager.entry_points", fake_entry_points)

    pm = PluginManager()
    with caplog.at_level(logging.WARNING):
        pm.load(DummyCore())

    assert list(pm.sensors) == ["dup"]
    assert any("Duplicate adapter name" in r.message for r in caplog.records)


def test_load_data_dicts(monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture) -> None:
    def good_data_dict() -> dict:
        return {"foo": 1}

    def bad_data_dict() -> dict:
        raise RuntimeError("boom")

    eps = [DummyEntryPoint(good_data_dict), DummyEntryPoint(bad_data_dict)]

    def fake_entry_points(group: str) -> list[DummyEntryPoint]:
        return eps if group == "arbolab.data_dicts" else []

    monkeypatch.setattr("arbolab.plugin_manager.entry_points", fake_entry_points)

    pm = PluginManager()
    with caplog.at_level(logging.ERROR):
        pm.load(DummyCore())

    assert pm.get_data_dict("good_data_dict") == {"foo": 1}
    assert any("Failed to load data dict" in r.message for r in caplog.records)


def test_load_warns_on_duplicate_data_dict(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def make_data_dict() -> dict:
        return {"foo": 1}

    eps = [
        DummyEntryPoint(make_data_dict, name="dup"),
        DummyEntryPoint(make_data_dict, name="dup"),
    ]

    def fake_entry_points(group: str) -> list[DummyEntryPoint]:
        return eps if group == "arbolab.data_dicts" else []

    monkeypatch.setattr("arbolab.plugin_manager.entry_points", fake_entry_points)

    pm = PluginManager()
    with caplog.at_level(logging.WARNING):
        pm.load(DummyCore())

    assert list(pm.data_dicts) == ["dup"]
    assert any("Duplicate data dict name" in r.message for r in caplog.records)
