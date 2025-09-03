"""Path utilities for working-directory aware file management.

Provides helpers to:
- Normalize user inputs (``str``/``Path``) to :class:`pathlib.Path`
- Ensure directories exist when creating paths inside the working directory
- Offer a small class wrapping conventional subdirectories (``logs/``, ``plots/``, ...)
"""

from __future__ import annotations

from os import PathLike as OSPathLike
from os import fspath
from pathlib import Path

__all__ = [
    "PathLike",
    "to_path",
    "ensure_dir",
    "WorkDir",
]


PathLike = str | Path | OSPathLike[str]


def to_path(p: PathLike | None) -> Path | None:
    """Convert user input to ``Path`` or return ``None``.

    Accepts ``str`` and any ``os.PathLike`` instance. Raises ``TypeError``
    with a clear message when the input cannot be converted.
    """
    if p is None:
        return None
    if isinstance(p, Path):
        return p
    try:
        return Path(fspath(p))
    except TypeError as exc:  # pragma: no cover - defensive
        raise TypeError(f"Expected str or os.PathLike object, got {type(p).__name__}") from exc


def ensure_dir(p: PathLike) -> Path:
    """Ensure directory ``p`` exists and return it as ``Path``."""
    path = to_path(p)
    if path is None:
        raise TypeError("path cannot be None")
    path.mkdir(parents=True, exist_ok=True)
    return path


class WorkDir:
    """Encapsulate a working directory with conventional subdirectories.

    The class ensures that the root directory exists and lazily creates
    common subdirectories such as ``logs`` or ``data`` on access.

    Parameters
    ----------
    root:
        Base path of the working directory.  ``None`` is allowed, but accessing
        any subdirectory in that case will raise :class:`ValueError`.
    """

    def __init__(self, root: PathLike | None) -> None:
        self.root: Path | None = to_path(root)
        if self.root is not None:
            ensure_dir(self.root)

    # ------------------------------------------------------------------
    def _require_root(self) -> Path:
        if self.root is None:
            raise ValueError("working directory not configured")
        return self.root

    # ------------------------------------------------------------------
    def subdir(self, name: str) -> Path:
        """Return and create a named subdirectory under :attr:`root`."""
        base = self._require_root()
        return ensure_dir(base / name)

    # ------------------------------------------------------------------
    @property
    def logs(self) -> Path:
        """Path to the ``logs`` subdirectory."""
        return self.subdir("logs")

    # ------------------------------------------------------------------
    @property
    def plots(self) -> Path:
        """Path to the ``plots`` subdirectory."""
        return self.subdir("plots")

    # ------------------------------------------------------------------
    @property
    def data(self) -> Path:
        """Path to the ``data`` subdirectory."""
        return self.subdir("data")

    # ------------------------------------------------------------------
    @property
    def db(self) -> Path:
        """Path to the ``db`` subdirectory."""
        return self.subdir("db")

    # ------------------------------------------------------------------
    def db_path(self, filename: str | None = None) -> Path:
        """Return the conventional DuckDB database file path."""
        base = self.db
        if filename is None:
            filename = f"{base.parent.name}.duckdb"
        return base / filename
