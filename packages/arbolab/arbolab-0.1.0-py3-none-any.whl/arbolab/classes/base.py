"""Base SQLAlchemy models and entity utilities."""

from __future__ import annotations

import os
from datetime import datetime
from uuid import uuid4

from sqlalchemy import JSON, DateTime, Integer, Sequence, String, func
from sqlalchemy.ext.mutable import MutableDict, MutableList
from sqlalchemy.orm import DeclarativeBase, Mapped, declared_attr, mapped_column

from .mixins import ExternalIdMixin

TABLE_PREFIX = os.getenv("ARBOLAB_DB__TABLE_PREFIX", "")


def table_name(name: str) -> str:
    """Return database table *name* with the configured prefix."""
    return f"{TABLE_PREFIX}{name}"


class Base(DeclarativeBase):
    """Base declarative class."""


class BaseEntity(ExternalIdMixin, Base):
    """Common attributes shared by all domain entities.

    Examples
    --------
    >>> project.add_tag("field")
    >>> project.update_metadata(unit="cm")
    >>> project.source_uri = "https://example.org/data.csv"
    >>> project.get_metadata("unit")
    'cm'
    """

    __abstract__ = True

    @declared_attr.directive
    def id(cls) -> Mapped[int]:
        """Integer primary key using a dedicated sequence per table."""
        seq = Sequence(f"{cls.__tablename__}_id_seq")
        return mapped_column(Integer, seq, server_default=seq.next_value(), primary_key=True)

    uuid: Mapped[str] = mapped_column(
        String(36), default=lambda: str(uuid4()), unique=True, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=func.now(), onupdate=func.now(), nullable=False
    )
    tags: Mapped[list[str]] = mapped_column(MutableList.as_mutable(JSON), default=list)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", MutableDict.as_mutable(JSON), default=dict
    )
    provenance: Mapped[dict[str, object]] = mapped_column(
        MutableDict.as_mutable(JSON), default=dict
    )

    def add_tag(self, tag: str) -> None:
        """Attach *tag* to the entity if not present."""
        if tag not in self.tags:
            self.tags.append(tag)

    def remove_tag(self, tag: str) -> None:
        """Remove *tag* from the entity if present."""
        if tag in self.tags:
            self.tags.remove(tag)

    def update_metadata(self, **entries: object) -> None:
        """Merge ``entries`` into the metadata dictionary."""
        self.metadata_.update(entries)

    def get_metadata(self, key: str, default: object | None = None) -> object | None:
        """Return the metadata value for ``key`` or ``default``."""
        return self.metadata_.get(key, default)

    @property
    def source_uri(self) -> str | None:
        """Optional URI pointing to the data source for this entity."""
        value = self.provenance.get("source_uri")
        return value if isinstance(value, str) else None

    @source_uri.setter
    def source_uri(self, value: str | None) -> None:
        if value is None:
            self.provenance.pop("source_uri", None)
        else:
            self.provenance["source_uri"] = value

    def __repr__(self) -> str:
        """Return a developer-friendly representation of the entity."""
        return f"{self.__class__.__name__}(id={self.id!r}, uuid={self.uuid!r})"

    def __str__(self) -> str:  # pragma: no cover - simple delegation
        """Return a readable string representation."""
        return self.__repr__()

    def __eq__(self, other: object) -> bool:
        """Compare entities by UUID and type."""
        if not isinstance(other, self.__class__):
            return NotImplemented
        return self.uuid == other.uuid

    def __hash__(self) -> int:
        """Hash based on the unique UUID."""
        return hash(self.uuid)


__all__ = ["Base", "BaseEntity", "table_name", "TABLE_PREFIX"]
