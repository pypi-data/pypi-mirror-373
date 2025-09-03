"""Reusable SQLAlchemy mixins for arbolab models."""

from __future__ import annotations

import uuid
from datetime import datetime, timezone

from sqlalchemy import JSON, DateTime, Enum, String
from sqlalchemy.orm import Mapped, declarative_mixin, mapped_column
from sqlalchemy.types import Uuid

from .status import Status


@declarative_mixin
class PrimaryKeyMixin:
    """Mixin providing a UUID primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False
    )


@declarative_mixin
class TimestampMixin:
    """Mixin providing created and updated timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),  # noqa: UP017
        onupdate=lambda: datetime.now(timezone.utc),  # noqa: UP017
        nullable=False,
    )


@declarative_mixin
class MetaMixin:
    """Mixin providing generic metadata fields."""

    name: Mapped[str | None] = mapped_column(String, nullable=True)
    description: Mapped[str | None] = mapped_column(String, nullable=True)
    tags: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    metadata_: Mapped[dict[str, object]] = mapped_column(
        "metadata", JSON, default=dict, nullable=False
    )
    provenance: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.DRAFT, nullable=False)


class ExternalIdMixin:
    """Mixin providing storage for system-specific external identifiers.

    External identifiers are stored in a JSON mapping where keys identify the
    external system (e.g. ``"sensor_serial"``) and values hold the respective
    identifier strings.
    """

    external_ids: Mapped[dict[str, str]] = mapped_column(JSON, default=dict, nullable=False)

    def set_external_id(self, system: str, value: str) -> None:
        """Register an identifier for an external system."""
        self.external_ids[system] = value

    def get_external_id(self, system: str) -> str | None:
        """Return the identifier for *system*, if present."""
        return self.external_ids.get(system)
