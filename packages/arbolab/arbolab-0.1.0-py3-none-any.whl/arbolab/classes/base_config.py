"""Configuration model stored in the database."""

from __future__ import annotations

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column

from .base import Base, table_name


class Config(Base):
    """Simple key-value configuration entry.

    The configuration is stored as a single JSON document in the ``value``
    column under the key ``"config"``.
    """

    __tablename__ = table_name("config")

    key: Mapped[str] = mapped_column(String, primary_key=True)
    value: Mapped[str] = mapped_column(Text, nullable=False)

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the configuration."""
        return f"Config(key={self.key!r}, value={self.value!r})"

    def __str__(self) -> str:  # pragma: no cover - simple delegation
        """Return a readable string representation."""
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        """Compare configuration entries by key and value."""
        if not isinstance(other, Config):
            return NotImplemented
        return self.key == other.key and self.value == other.value

    def __hash__(self) -> int:
        """Hash based on key and value."""
        return hash((self.key, self.value))
