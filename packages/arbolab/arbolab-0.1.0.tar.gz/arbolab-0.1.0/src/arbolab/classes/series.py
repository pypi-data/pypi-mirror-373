"""Database model representing a measurement series."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseEntity, table_name

if TYPE_CHECKING:  # pragma: no cover - imports for type checking only
    from .measurement import Measurement
    from .project import Project


class Series(BaseEntity):
    """A series within a project."""

    __tablename__ = table_name("series")

    __table_args__ = (
        UniqueConstraint("project_id", "name"),
        UniqueConstraint("id", "project_id"),
    )

    project_id: Mapped[int] = mapped_column(ForeignKey(f"{table_name('projects')}.id"))
    name: Mapped[str] = mapped_column(String)

    project: Mapped[Project] = relationship(back_populates="series")
    measurements: Mapped[list[Measurement]] = relationship(
        back_populates="series",
        cascade="all, delete-orphan",
        overlaps="measurements,project,sensor",
    )
