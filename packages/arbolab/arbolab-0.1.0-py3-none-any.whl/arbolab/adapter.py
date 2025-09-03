"""Public adapter interfaces and core service contract.

Sensors (ls, tcc, tms, ptq) MUST import from this module only. They must NOT
import from ``arbolab.lab`` or ``arbolab.log.*`` to avoid circular
dependencies and tight coupling. Core wires dependencies via ``Adapter.attach``
with a narrow ``CoreServices`` interface.
"""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Protocol, runtime_checkable

if TYPE_CHECKING:  # typing-only imports to avoid runtime cycles
    from .config import Config
    from .db import DBManager
    from .plotting.plotter import Plotter


class CoreServices(Protocol):
    """Narrow facade of core services available to sensor adapters.

    Adapters should keep references to the services they need and should not
    attempt to import internal modules from arbolab.
    """

    @property
    def logger(self) -> logging.Logger:
        """Return the base project logger."""

    @property
    def config(self) -> Config:
        """Return the active project configuration."""

    @property
    def db(self) -> DBManager:
        """Return the database manager."""

    @property
    def plotter(self) -> Plotter:
        """Return the plotting utility."""


@runtime_checkable
class Adapter(Protocol):
    """Service Provider Interface for sensor packages.

    Required usage rules for sensor packages:
    - Import this Protocol from ``arbolab.adapter`` only.
    - Do NOT import from ``arbolab.lab`` or ``arbolab.log``.
    - Receive dependencies via ``attach(core: CoreServices)`` and store only
      what you need (e.g., a logger child, db handle, etc.).
    """

    #: Unique, short adapter name (e.g. "ls", "tms", "tcc", "ptq").
    name: str

    def attach(self, core: CoreServices) -> None:
        """Attach core services provided by the application."""


__all__ = ["Adapter", "CoreServices"]
