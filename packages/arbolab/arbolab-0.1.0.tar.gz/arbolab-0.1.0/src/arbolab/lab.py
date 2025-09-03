"""Core Lab wiring, plugin loading and persistence."""

from __future__ import annotations

import logging
from collections.abc import Iterable
from dataclasses import dataclass, field
from pathlib import Path
from types import TracebackType

from sqlalchemy.exc import ProgrammingError, SQLAlchemyError

from .adapter import Adapter
from .log import setup_logging
from .config import Config
from .db import DBManager
from .persistence import ConfigStore
from .plotting import Plotter
from .plugin_manager import PluginManager
from .utils import path as pathutil
from .utils.path import PathLike


@dataclass
class Lab:
    """Laboratory container managing configuration, DB and plugins."""

    config: Config = field(default_factory=Config.from_env)
    config_store: ConfigStore | None = None
    logger: logging.Logger = field(init=False)
    db: DBManager = field(init=False)
    plotter: Plotter = field(init=False)
    plugins: PluginManager = field(default_factory=PluginManager)

    # ------------------------------------------------------------------
    @property
    def sensors(self) -> dict[str, Adapter]:
        """Mapping of registered sensor adapters."""
        return self.plugins.sensors

    def __post_init__(self) -> None:
        """Initialise logging, database connection and plotting helper."""
        self.logger = setup_logging(
            config=self.config.logging,
            working_directory=self.config.working_dir,
        )
        if self.config.db_url is None:
            raise ValueError("config.db_url must be set")
        if self.config_store is None:
            self.db = DBManager(self.config.db_url, config=self.config.db)
            self.config_store = ConfigStore(self.db)
        else:
            self.db = self.config_store.db
        self.db.ensure_meta()
        self.config.plot.apply()
        self.plotter = Plotter()

    def _reconfigure_logging(self, log_changed: bool, logging_changed: bool) -> None:
        """Adjust logging when configuration changes."""
        if logging_changed:
            self.logger = setup_logging(
                config=self.config.logging,
                working_directory=self.config.working_dir,
            )
        elif log_changed:
            level = self.config.log_level
            if level == "NONE":
                logging.disable(logging.CRITICAL)
            else:
                logging.disable(logging.NOTSET)
                if level:
                    self.logger.setLevel(level)
                    for handler in self.logger.handlers:
                        handler.setLevel(level)

    def _reconfigure_db(self, db_changed: bool) -> None:
        """Recreate the database manager if the URL or config changed."""
        if not db_changed:
            return
        # Explicitly dispose the old engine to avoid resource leaks
        self.db.engine.dispose()
        if self.config.db_url is None:
            raise ValueError("config.db_url must be set")
        try:
            self.db = DBManager(self.config.db_url, config=self.config.db)
            self.db.ensure_meta()
            self.config_store = ConfigStore(self.db)
        except ProgrammingError as exc:
            if "Type with name SERIAL" in str(exc) and self.config.db_url.startswith("duckdb://"):
                raise RuntimeError(
                    "DuckDB version is incompatible (missing SERIAL type). "
                    "Please upgrade DuckDB."
                ) from exc
            raise

    def _reconfigure_plot(self, plot_changed: bool) -> None:
        """Recreate the plotting helper after configuration changes."""
        if plot_changed:
            self.config.plot.apply()
            self.plotter = Plotter()

    def _persist_config(self) -> None:
        """Store the current configuration using the :class:`ConfigStore`."""
        self.config_store.save(self.config)

    # ------------------------------------------------------------------
    def update_config(self, **changes: object) -> None:
        """Update configuration fields and reconfigure helpers.

        Parameters
        ----------
        **changes:
            Mapping of ``Config`` field names to their new values.

        Notes
        -----
        Changes to the working directory trigger a logging reconfiguration.
        """
        valid_keys = set(type(self.config).model_fields) | {"log_level"}
        unknown = set(changes) - valid_keys
        if unknown:
            raise AttributeError("Unknown config field: " + ", ".join(sorted(unknown)))
        if "log_level" in changes and changes["log_level"] is None:
            changes.pop("log_level")

        update_fields = {
            key: value for key, value in changes.items() if key in type(self.config).model_fields
        }
        if update_fields:
            self.config = self.config.model_copy(update=update_fields)
        if "log_level" in changes:
            self.config.log_level = changes["log_level"]

        changed = set(changes)

        # Determine which configuration sections were modified
        db_changed = bool(changed & {"db_url", "db"})
        plot_changed = "plot" in changed
        log_changed = "log_level" in changed
        logging_cfg_changed = "logging" in changed
        working_dir_changed = "working_dir" in changed

        # Reconfigure affected helpers explicitly for clarity
        if db_changed:
            self._reconfigure_db(True)
        if plot_changed:
            self._reconfigure_plot(True)
        if log_changed or logging_cfg_changed or working_dir_changed:
            self._reconfigure_logging(log_changed, logging_cfg_changed or working_dir_changed)

        self._persist_config()

    # ------------------------------------------------------------------
    def check_integrity(self) -> list[str]:
        """Verify consistency between database records and data files.

        Returns
        -------
        list[str]
            Descriptions of all problems found. An empty list indicates the
            storage is consistent.
        """
        from sqlalchemy import select

        from .classes.data import DATA_DIR, Data

        issues: list[str] = []
        files: set[Path] = set()

        with self.db.session() as sess:
            data_entries: Iterable[Data] = sess.execute(select(Data)).scalars()
            for entry in data_entries:
                path = Path(entry.path)
                files.add(path.resolve())
                if not path.exists():
                    issues.append(f"Missing data file for id {entry.id}: {path}")
                    continue
                fmt = entry.format or "parquet"
                if fmt == "parquet" and path.suffix != ".parquet":
                    issues.append(f"Data id {entry.id} expects parquet file, got {path.suffix}")
                if fmt == "feather" and path.suffix != ".feather":
                    issues.append(f"Data id {entry.id} expects feather file, got {path.suffix}")

        # Detect orphaned files in the data directory
        if DATA_DIR.exists():
            for file in DATA_DIR.iterdir():
                if (
                    file.is_file()
                    and file.suffix in {".parquet", ".feather"}
                    and file.resolve() not in files
                ):
                    issues.append(f"Orphan data file: {file}")

        for msg in issues:
            self.logger.warning(msg)

        return issues

    # ------------------------------------------------------------------
    def _initialize_plugins_and_verify(self, load_plugins: bool, verify: bool) -> None:
        """Load plugins and optionally run an integrity check."""
        if load_plugins:
            self.plugins.load(self)
            self.logger.info("Lab loaded with %d sensor(s)", len(self.plugins.sensors))
        if verify:
            self.check_integrity()

    # ------------------------------------------------------------------
    def close(self, *, verify: bool = True) -> None:
        """Dispose resources and optionally verify integrity."""
        if verify:
            self.check_integrity()
        # Explicitly dispose the underlying engine to close connections
        self.db.engine.dispose()

    # ------------------------------------------------------------------
    def __enter__(self) -> Lab:  # pragma: no cover - simple delegation
        """Return ``self`` to support ``with`` statements."""
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc: BaseException | None,
        tb: TracebackType | None,
    ) -> None:  # pragma: no cover - simple delegation
        """Ensure the lab is closed when leaving a ``with`` block."""
        self.close()

    # ------------------------------------------------------------------
    @classmethod
    def setup(
        cls,
        config: Config | None = None,
        *,
        load_plugins: bool = True,
        plugin_manager: PluginManager | None = None,
        verify: bool = True,
    ) -> Lab:
        """Create a new Lab and persist its configuration.

        Parameters
        ----------
        config:
            Optional configuration to initialise the lab with. If ``None`` the
            configuration is loaded from the environment.
        load_plugins:
            Whether adapter plugins should be loaded immediately.
        plugin_manager:
            Custom plugin manager instance to use. If omitted, a default
            :class:`PluginManager` is created.
        verify:
            When ``True`` perform a storage integrity check after setup.
        """
        cfg = config or Config.from_env()
        db_path: Path | None = None
        if cfg.db_url is None:
            workdir = cfg.working_dir or Path.cwd()
            db_name = f"{workdir.name}.duckdb"
            db_path = workdir / db_name
            cfg.db_url = f"duckdb:///{db_path}"
        elif cfg.db_url.startswith("duckdb:///"):
            db_path = Path(cfg.db_url.removeprefix("duckdb:///"))

        if db_path and db_path.exists():
            logging.warning("Lab already exists at %s, loading existing lab", db_path)
            return cls.load(db_path, load_plugins=load_plugins, plugin_manager=plugin_manager)
        try:
            lab = cls(cfg, plugins=plugin_manager or PluginManager())
        except ProgrammingError as exc:
            # Older DuckDB versions without SERIAL support are not supported
            if "Type with name SERIAL" in str(exc) and cfg.db_url.startswith("duckdb://"):
                raise RuntimeError(
                    "DuckDB version is incompatible (missing SERIAL type). Please upgrade DuckDB."
                ) from exc
            raise

        lab.config_store.save(cfg)
        lab._initialize_plugins_and_verify(load_plugins, verify)
        return lab

    # ------------------------------------------------------------------
    @classmethod
    def load(
        cls,
        db_path: PathLike,
        *,
        load_plugins: bool = True,
        plugin_manager: PluginManager | None = None,
        verify: bool = True,
    ) -> Lab:
        """Load an existing Lab from the given DuckDB database file.

        Parameters
        ----------
        db_path:
            Path to the DuckDB database file to load.
        load_plugins:
            Whether adapter plugins should be loaded immediately.
        plugin_manager:
            Custom plugin manager instance to use. If omitted, a default
            :class:`PluginManager` is created.
        verify:
            When ``True`` perform a storage integrity check after loading.
        """
        db_path = pathutil.to_path(db_path)
        if db_path is None:  # pragma: no cover - input type enforced
            raise TypeError("db_path must be a valid path")
        if not db_path.exists():
            raise FileNotFoundError(f"Database file not found: {db_path}")
        db_url = f"duckdb:///{db_path}"
        try:
            manager = DBManager(db_url)
            store = ConfigStore(manager)
            cfg = store.load()
        except SQLAlchemyError as exc:
            # Only DuckDB databases are supported
            raise RuntimeError(f"Failed to load DuckDB database from {db_path}") from exc
        cfg.db_url = db_url

        # Use the provided plugin manager or create a default one
        plugins = plugin_manager or PluginManager()
        lab = cls(cfg, config_store=store, plugins=plugins)
        lab._initialize_plugins_and_verify(load_plugins, verify)
        return lab
