import builtins
import sys
import types

import pytest


def test_plot_config_apply_raises_when_matplotlib_missing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setitem(sys.modules, "numpy", types.ModuleType("numpy"))
    monkeypatch.setitem(sys.modules, "pandas", types.ModuleType("pandas"))

    from arbolab.config import PlotConfig
    from arbolab.exceptions import MissingOptionalDependency

    real_import = builtins.__import__

    def fake_import(name: str, *args: object, **kwargs: object) -> types.ModuleType:
        if name.startswith("matplotlib"):
            raise ImportError("missing")
        return real_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", fake_import)

    cfg = PlotConfig(backend="Agg")
    with pytest.raises(MissingOptionalDependency):
        cfg.apply()


def test_plot_config_apply_runs_with_stub_matplotlib(
    monkeypatch: pytest.MonkeyPatch,
) -> None:

    monkeypatch.setitem(sys.modules, "numpy", types.ModuleType("numpy"))
    monkeypatch.setitem(sys.modules, "pandas", types.ModuleType("pandas"))

    from arbolab.config import PlotConfig

    matplotlib = types.ModuleType("matplotlib")

    def use(name: str) -> None:
        matplotlib.used_backend = name

    matplotlib.use = use

    pyplot = types.ModuleType("matplotlib.pyplot")

    class _Style:
        def use(self, style: str) -> None:
            self.used_style = style

    pyplot.style = _Style()

    monkeypatch.setitem(sys.modules, "matplotlib", matplotlib)
    monkeypatch.setitem(sys.modules, "matplotlib.pyplot", pyplot)

    cfg = PlotConfig(backend="Agg", style="default")
    cfg.apply()

    assert matplotlib.used_backend == "Agg"
    assert pyplot.style.used_style == "default"
