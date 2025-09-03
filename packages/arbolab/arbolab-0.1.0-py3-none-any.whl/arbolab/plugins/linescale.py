"""Lazy import wrapper for the line scale adapter.

This module defers importing ``arbolab_linescale`` until an attribute is
actually accessed.  If the package is missing, a helpful error is raised
instructing the user to install the required extra.
"""

from __future__ import annotations

from ..utils.lazy_import import lazy_module

__getattr__ = lazy_module("arbolab_linescale", extra="linescale")

__all__ = ["__getattr__"]
