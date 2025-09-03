"""Database model for trees in a project."""

from __future__ import annotations

from datetime import datetime
from math import pi
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseEntity, table_name

if TYPE_CHECKING:  # pragma: no cover - imports for type checking only
    from .project import Project
    from .sensor import Sensor
    from .sensor_position import SensorPosition
    from .tree_species import TreeSpecies


class Tree(BaseEntity):
    """Represent a tree within a project."""

    __tablename__ = table_name("trees")

    __table_args__ = (UniqueConstraint("project_id", "name"),)

    project_id: Mapped[int] = mapped_column(ForeignKey(f"{table_name('projects')}.id"))
    name: Mapped[str] = mapped_column(String)
    datetime_survey: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    tree_species_id: Mapped[int | None] = mapped_column(
        ForeignKey(f"{table_name('tree_species')}.id")
    )
    circumference: Mapped[float | None] = mapped_column(Float)
    height: Mapped[float | None] = mapped_column(Float)
    fork_height: Mapped[float | None] = mapped_column(Float)

    project: Mapped[Project] = relationship(back_populates="trees")
    sensor_positions: Mapped[list[SensorPosition]] = relationship(back_populates="tree")
    sensors: Mapped[list[Sensor]] = relationship(
        back_populates="tree", cascade="all, delete-orphan"
    )
    tree_species: Mapped[TreeSpecies | None] = relationship(back_populates="trees")

    @property
    def diameter(self) -> float | None:
        """Return the diameter derived from the circumference."""
        if self.circumference is None:
            return None
        return self.circumference / pi
