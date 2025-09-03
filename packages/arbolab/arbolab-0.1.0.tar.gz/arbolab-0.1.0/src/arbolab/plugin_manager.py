"""Plugin management for arbolab adapters and data dictionaries."""

from __future__ import annotations

from importlib.metadata import EntryPoint, entry_points

from .adapter import Adapter, CoreServices


class PluginManager:
    """Discover and register adapter and data dictionary plugins."""

    def __init__(self) -> None:
        self.sensors: dict[str, Adapter] = {}
        self.data_dicts: dict[str, dict] = {}

    # ------------------------------------------------------------------
    def register(self, adapter: Adapter) -> None:
        """Register a single adapter instance.

        Raises
        ------
        ValueError
            If an adapter with the same ``name`` is already registered.
        """

        if adapter.name in self.sensors:
            raise ValueError(f"Duplicate adapter name: {adapter.name}")
        self.sensors[adapter.name] = adapter

    # ------------------------------------------------------------------
    def register_data_dict(self, name: str, data_dict: dict) -> None:
        """Register a single data dictionary.

        Raises
        ------
        ValueError
            If a data dictionary with the same ``name`` is already registered.
        """

        if name in self.data_dicts:
            raise ValueError(f"Duplicate data dict name: {name}")
        self.data_dicts[name] = data_dict

    # ------------------------------------------------------------------
    def get_data_dict(self, name: str) -> dict:
        """Return the registered data dictionary with ``name``."""

        return self.data_dicts[name]

    # ------------------------------------------------------------------
    def _load_adapter(
        self,
        core: CoreServices,
        ep: EntryPoint,
    ) -> None:
        """Load a single adapter from an entry point."""

        try:
            adapter_cls = ep.load()
            adapter: Adapter = adapter_cls()
            adapter.attach(core)
            self.register(adapter)
        except ValueError as exc:
            core.logger.warning("Skipping adapter %s from %s: %s", ep.name, ep.value, exc)
        except Exception as exc:  # pragma: no cover - defensive
            core.logger.error("Failed to load adapter %s from %s: %s", ep.name, ep.value, exc)
        else:
            core.logger.info("Loaded adapter: %s", adapter.name)

    # ------------------------------------------------------------------
    def _load_data_dict(self, core: CoreServices, ep: EntryPoint) -> None:
        """Load and register a data dictionary."""

        try:
            loader = ep.load()
            data_dict = loader()
            self.register_data_dict(ep.name, data_dict)
        except ValueError as exc:
            core.logger.warning("Skipping data dict %s from %s: %s", ep.name, ep.value, exc)
        except Exception as exc:  # pragma: no cover - defensive
            core.logger.error("Failed to load data dict %s from %s: %s", ep.name, ep.value, exc)
        else:
            core.logger.info("Loaded data dict: %s", ep.name)

    # ------------------------------------------------------------------
    def load(self, core: CoreServices, *, group: str = "arbolab.adapters") -> None:
        """Load adapters and data dictionaries from entry points."""

        for ep in entry_points(group=group):
            self._load_adapter(core, ep)

        for ep in entry_points(group="arbolab.data_dicts"):
            self._load_data_dict(core, ep)


__all__ = ["PluginManager"]
