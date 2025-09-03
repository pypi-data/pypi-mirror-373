"""Lazy import wrapper for the tree motion adapter.

Accessing attributes of this module triggers loading of the optional
``arbolab_treemotion`` package.  If it is not installed a clear error is
raised guiding the user to install the ``treemotion`` extra.
"""

from __future__ import annotations

from ..utils.lazy_import import lazy_module

__getattr__ = lazy_module("arbolab_treemotion", extra="treemotion")

__all__ = ["__getattr__"]
