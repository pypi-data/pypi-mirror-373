"""Unified plotter for different backends."""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from functools import singledispatchmethod
from pathlib import Path
from typing import TYPE_CHECKING

from ..log import get_logger
from ..exceptions import MissingOptionalDependency

if TYPE_CHECKING:  # pragma: no cover - typing only
    from matplotlib.axes import Axes
    from matplotlib.figure import Figure as MplFigure
    from matplotlib.figure import SubFigure
    from plotly.graph_objects import Figure as PlotlyFigure

logger = get_logger(__name__)


def _slugify(text: str | None) -> str:
    """Return a filesystem-friendly version of *text*.

    Parameters
    ----------
    text:
        The string to slugify. ``None`` results in an empty string.
    """
    if not text:
        return ""
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9_-]+", "_", text)
    return text.strip("_")


@dataclass(slots=True)
class Plotter:
    """Handle Matplotlib, Seaborn and Plotly figures.

    Parameters
    ----------
    directory:
        Base directory where plots will be stored. Created on initialisation.
    figsize:
        Default figure size in inches.
    dpi:
        Rendering resolution for saved figures.
    seaborn_style:
        Style name passed to :mod:`seaborn` when available.
    color_palette:
        Name of the color palette used by :mod:`seaborn`.
    plotly_template:
        Default template used for :mod:`plotly` figures.
    grid:
        Toggle grid display for supported backends.
    """

    directory: Path = field(default_factory=lambda: Path("plots"))
    figsize: tuple[float, float] = (8.0, 6.0)
    dpi: int = 300
    seaborn_style: str = "whitegrid"
    color_palette: str = "bright"
    plotly_template: str = "plotly_white"
    grid: bool = True

    def __post_init__(self) -> None:
        """Prepare plotting backends and ensure the output directory exists."""
        self.directory.mkdir(parents=True, exist_ok=True)
        self._apply_matplotlib_defaults()
        self._apply_plotly_defaults()

    # ------------------------------------------------------------------
    # configuration helpers
    def _apply_matplotlib_defaults(self) -> None:
        try:
            import matplotlib.pyplot as plt
        except ImportError as exc:  # pragma: no cover - dependency missing
            raise MissingOptionalDependency("matplotlib", "plot") from exc
        plt.rcParams["figure.figsize"] = self.figsize
        plt.rcParams["axes.grid"] = self.grid
        plt.rcParams["savefig.dpi"] = self.dpi

        try:
            import seaborn as sns
        except ImportError:  # pragma: no cover - optional
            logger.debug("Seaborn not available; skipping style setup")
        else:
            try:
                sns.set_style(self.seaborn_style)
                sns.set_palette(self.color_palette)
            except Exception as exc:  # pragma: no cover - stylistic errors
                logger.warning("Failed to apply seaborn configuration: %s", exc)

    def _apply_plotly_defaults(self) -> None:
        try:
            import plotly.io as pio
        except ImportError:  # pragma: no cover - optional
            logger.debug("Plotly not available; skipping template setup")
            return
        pio.templates.default = self.plotly_template

    # ------------------------------------------------------------------
    # saving
    def save(
        self,
        plot: object,
        filename: str,
        *,
        subdir: str | None = None,
        format: str = "png",
        close: bool = True,
    ) -> Path:
        """Save a *plot* to *filename* within *directory*.

        The plot type is detected and handled via single dispatch. Plotly figures
        are stored as HTML files while Matplotlib/Seaborn figures are saved as
        image files using ``format``.
        """
        dir_path = self._ensure_subdir(subdir)
        fname = _slugify(filename)
        path = dir_path / fname
        return self._save(plot, path, format=format, close=close)

    @singledispatchmethod
    def _save(
        self, plot: object, path: Path, *, format: str, close: bool
    ) -> Path:  # pragma: no cover - base case
        raise TypeError(f"Unsupported plot object: {type(plot)!r}")

    def _save_plotly(self, plot: object, path: Path) -> Path:
        """Save a Plotly *plot* as HTML to *path*."""
        fig = self._to_plotly_figure(plot)
        self._update_plotly_layout(fig)
        fig.write_html(path)
        return path

    def _save_matplotlib(self, plot: object, path: Path, *, close: bool = True) -> Path:
        """Save a Matplotlib *plot* to *path* respecting *close* behavior."""
        fig = self._to_matplotlib_figure(plot)
        fig.savefig(path, dpi=self.dpi)
        if close:
            self._close_matplotlib(fig)
        return path

    # ------------------------------------------------------------------
    # internal utilities
    def _ensure_subdir(self, subdir: str | None) -> Path:
        path = self.directory / _slugify(subdir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def _to_plotly_figure(self, plot: object) -> PlotlyFigure:
        try:
            from plotly.graph_objects import Figure
        except ImportError as exc:  # pragma: no cover - dependency missing
            raise MissingOptionalDependency("plotly", "plot") from exc
        if not isinstance(plot, Figure):
            raise TypeError(f"Unsupported plotly plot object: {type(plot)!r}")
        return plot

    def _to_matplotlib_figure(self, plot: object) -> MplFigure:
        try:
            from matplotlib.axes import Axes
            from matplotlib.figure import Figure, SubFigure
        except ImportError as exc:  # pragma: no cover - dependency missing
            raise MissingOptionalDependency("matplotlib", "plot") from exc
        if isinstance(plot, SubFigure):
            from typing import cast

            return cast("MplFigure", plot.figure)
        if isinstance(plot, Figure) and not isinstance(plot, SubFigure):
            from typing import cast

            return cast("MplFigure", plot)
        if isinstance(plot, Axes):
            return plot.figure
        raise TypeError(f"Unsupported plot object: {type(plot)!r}")

    def _update_plotly_layout(self, fig: PlotlyFigure) -> None:
        width = int(self.figsize[0] * self.dpi)
        height = int(self.figsize[1] * self.dpi)
        fig.update_layout(width=width, height=height)
        fig.update_xaxes(showgrid=self.grid)
        fig.update_yaxes(showgrid=self.grid)

    def _close_matplotlib(self, fig: MplFigure) -> None:
        try:
            import matplotlib.pyplot as plt
        except Exception:  # pragma: no cover - dependency missing
            return
        try:
            plt.close(fig)
        except Exception:  # pragma: no cover - generic guard
            logger.debug("Failed to close matplotlib figure", exc_info=True)


# ------------------------------------------------------------------
# dispatch registrations
try:  # pragma: no cover - optional
    from plotly.graph_objects import Figure as _PlotlyFigure
except Exception:  # pragma: no cover - optional
    pass
else:

    @Plotter._save.register(_PlotlyFigure)  # type: ignore[misc]
    def _(self: Plotter, plot: PlotlyFigure, path: Path, *, format: str, close: bool) -> Path:
        return self._save_plotly(plot, path.with_suffix(".html"))


try:  # pragma: no cover - optional
    from matplotlib.axes import Axes as _Axes
    from matplotlib.figure import Figure as _MplFigure
    from matplotlib.figure import SubFigure as _SubFigure
except Exception:  # pragma: no cover - optional
    pass
else:

    @Plotter._save.register(_MplFigure)  # type: ignore[misc]
    def _(self: Plotter, plot: MplFigure, path: Path, *, format: str, close: bool) -> Path:
        return self._save_matplotlib(plot, path.with_suffix(f".{format}"), close=close)

    @Plotter._save.register(_Axes)  # type: ignore[misc]
    def _(self: Plotter, plot: Axes, path: Path, *, format: str, close: bool) -> Path:
        return self._save_matplotlib(plot, path.with_suffix(f".{format}"), close=close)

    @Plotter._save.register(_SubFigure)  # type: ignore[misc]
    def _(self: Plotter, plot: SubFigure, path: Path, *, format: str, close: bool) -> Path:
        return self._save_matplotlib(plot, path.with_suffix(f".{format}"), close=close)
