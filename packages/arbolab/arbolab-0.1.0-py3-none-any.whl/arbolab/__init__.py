"""Public package interface for arbolab."""

from __future__ import annotations

from .classes.project import Project
from .config import Config
from .lab import Lab

__all__ = ["Lab", "Project", "setup"]


def setup(config: Config | None = None, *, load_plugins: bool = True) -> Lab:
    """Create and configure a :class:`Lab` instance."""
    return Lab.setup(config=config, load_plugins=load_plugins)
