"""Lazy import wrapper for the tree cable calculation adapter.

This module defers importing ``arbolab_treecablecalc`` until an attribute is
accessed. If the package is missing a helpful error is raised instructing the
user to install the ``treecablecalc`` extra.
"""

from __future__ import annotations

from ..utils.lazy_import import lazy_module

__getattr__ = lazy_module("arbolab_treecablecalc", extra="treecablecalc")

__all__ = ["__getattr__"]
