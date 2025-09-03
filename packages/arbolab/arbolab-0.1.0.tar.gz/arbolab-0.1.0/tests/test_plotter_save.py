from pathlib import Path

import matplotlib.pyplot as plt
import pytest

go = pytest.importorskip("plotly.graph_objects")

from arbolab.plotting.plotter import Plotter


def test_save_matplotlib_direct(tmp_path: Path) -> None:
    fig, ax = plt.subplots()
    ax.plot([1, 2], [3, 4])
    plotter = Plotter(directory=tmp_path)
    path = tmp_path / "fig.png"
    returned = plotter._save_matplotlib(fig, path)
    assert returned == path
    assert path.is_file()


def test_save_plotly_direct(tmp_path: Path) -> None:
    fig = go.Figure(data=go.Scatter(x=[1, 2], y=[3, 4]))
    plotter = Plotter(directory=tmp_path)
    path = tmp_path / "fig.html"
    returned = plotter._save_plotly(fig, path)
    assert returned == path
    assert path.is_file()


def test_save_dispatch_matplotlib(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    fig, ax = plt.subplots()
    plotter = Plotter(directory=tmp_path)
    called: dict[str, Path] = {}

    def fake_save(
        self: Plotter, plot: object, path: Path, *, close: bool = True
    ) -> Path:
        called["path"] = path
        return path

    monkeypatch.setattr(Plotter, "_save_matplotlib", fake_save)
    result = plotter.save(fig, "fig")
    expected = tmp_path / "fig.png"
    assert result == expected
    assert called["path"] == expected


def test_save_dispatch_plotly(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    fig = go.Figure(data=go.Scatter(x=[1], y=[1]))
    plotter = Plotter(directory=tmp_path)
    called: dict[str, Path] = {}

    def fake_save(self: Plotter, plot: object, path: Path) -> Path:
        called["path"] = path
        return path

    monkeypatch.setattr(Plotter, "_save_plotly", fake_save)
    result = plotter.save(fig, "fig")
    expected = tmp_path / "fig.html"
    assert result == expected
    assert called["path"] == expected
