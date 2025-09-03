"""Utility helpers shared across :mod:`arbolab` packages.

Some helpers depend on :mod:`pandas` but the library is considered an optional
dependency.  To avoid importing it unnecessarily, the functions are loaded
lazy on first access via :func:`__getattr__`.  They can still be imported
directly from :mod:`arbolab.utils` or from their respective submodules.
"""

from __future__ import annotations

from importlib import import_module

_PANDAS_FUNCS: dict[str, str] = {
    "calc_sample_rate": ".dataframe",
    "calc_amplitude": ".dataframe",
    "calc_min_max": ".dataframe",
    "validate_time_format": ".dataframe",
    "time_cut_by_datetime_index": ".dataframe",
    "validate_df": ".dataframe",
    "load_data_dict": ".data_dict",
    "validate_dataframe": ".data_dict",
}


def __getattr__(name: str) -> object:  # pragma: no cover - thin wrapper
    """Lazy import attributes from the relevant :mod:`arbolab.utils` submodule.

    This function is called by Python when a non-existent attribute is accessed
    on the :mod:`arbolab.utils` package.  If *name* matches one of the known
    helper functions, the attribute is loaded from the configured submodule and
    cached on this module for subsequent lookups.
    """
    module_name = _PANDAS_FUNCS.get(name)
    if module_name is not None:
        module = import_module(module_name, __name__)
        attr = getattr(module, name)
        globals()[name] = attr  # Cache for future attribute access
        return attr
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list[str]:  # pragma: no cover - helper for interactive use
    return sorted(list(globals().keys()) + list(_PANDAS_FUNCS))


# ``__all__`` intentionally does not expose the lazy DataFrame helpers so that
# ``from arbolab.utils import *`` does not implicitly import ``pandas``.
__all__: list[str] = []
