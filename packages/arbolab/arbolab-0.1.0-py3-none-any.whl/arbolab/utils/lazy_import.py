"""Generic helpers for lazily importing optional modules."""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from types import ModuleType

from arbolab.exceptions import MissingOptionalDependency

__all__ = ["lazy_module"]


def lazy_module(module: str, extra: str) -> Callable[[str], object]:
    """Return a ``__getattr__`` function that lazily loads *module*.

    Parameters
    ----------
    module:
        The fully qualified name of the optional module to import.
    extra:
        Name of the setuptools extra that provides the optional dependency.

    The returned callable is intended to be assigned to ``__getattr__`` at the
    module level so that accessing attributes triggers the import of *module*.
    If the import fails, :class:`~arbolab.exceptions.MissingOptionalDependency`
    is raised with a helpful installation message.
    """

    def _load() -> ModuleType:
        try:
            return import_module(module)
        except ModuleNotFoundError as exc:  # pragma: no cover - defensive
            raise MissingOptionalDependency(module, extra) from exc

    def __getattr__(name: str) -> object:  # pragma: no cover - simple delegation
        loaded = _load()
        return getattr(loaded, name)

    return __getattr__
