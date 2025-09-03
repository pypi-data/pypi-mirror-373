"""Store and retrieve configuration values in the database."""

from __future__ import annotations

from duckdb_engine import insert
from sqlalchemy import select

from ..classes.base_config import Config as ConfigEntry
from ..config import Config
from ..db import DBManager


class ConfigStore:
    """Persist configuration settings using a :class:`DBManager`."""

    def __init__(self, db: DBManager) -> None:
        self.db = db

    # ------------------------------------------------------------------
    def save(self, config: Config) -> None:
        """Persist the complete configuration as a JSON document."""
        self._store({"config": config.model_dump_json()})

    # ------------------------------------------------------------------
    def load(self) -> Config:
        """Load the configuration from the database."""
        with self.db.session() as sess:
            row = sess.scalar(select(ConfigEntry).where(ConfigEntry.key == "config"))
        if row is None:
            return Config()
        return Config.model_validate_json(row.value)

    # ------------------------------------------------------------------
    def _store(self, mapping: dict[str, str]) -> None:
        """Insert or update configuration entries in the database."""
        mapping = {k: v for k, v in mapping.items() if v is not None}
        if not mapping:
            return
        with self.db.session() as sess:
            stmt = insert(ConfigEntry).values(
                [{"key": key, "value": value} for key, value in mapping.items()]
            )
            stmt = stmt.on_conflict_do_update(
                index_elements=[ConfigEntry.key], set_={"value": stmt.excluded.value}
            )
            sess.execute(stmt)
            sess.commit()
