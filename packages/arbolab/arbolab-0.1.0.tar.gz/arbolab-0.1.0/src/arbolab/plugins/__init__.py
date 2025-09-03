"""Lazy import wrappers for optional plugins.

Each module in this package exposes a lazy import proxy for a
corresponding optional dependency. Importing from ``arbolab.plugins``
keeps the main package namespace clean while still providing convenient
access to the plugin wrappers.
"""

__all__ = [
    "linescale",
    "treemotion",
    "treeqinetic",
    "treecablecalc",
    "wind",
]
