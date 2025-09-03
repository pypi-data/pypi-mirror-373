"""Lazy import wrapper for the wind adapter.

This module defers importing ``arbolab_wind`` until an attribute is
accessed. If the package is missing a helpful error is raised instructing the
user to install the ``wind`` extra.
"""

from __future__ import annotations

from ..utils.lazy_import import lazy_module

__getattr__ = lazy_module("arbolab_wind", extra="wind")

__all__ = ["__getattr__"]
