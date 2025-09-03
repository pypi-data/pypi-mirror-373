"""Database model describing sensor placement on a tree."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseEntity, table_name

if TYPE_CHECKING:  # pragma: no cover - imports for type checking only
    from .project import Project
    from .sensor import Sensor
    from .tree import Tree


class SensorPosition(BaseEntity):
    """Sensor placement on a tree."""

    __tablename__ = table_name("sensor_positions")
    __table_args__ = (UniqueConstraint("tree_id", "height", "direction", "diameter"),)

    project_id: Mapped[int] = mapped_column(ForeignKey(f"{table_name('projects')}.id"))
    tree_id: Mapped[int] = mapped_column(ForeignKey(f"{table_name('trees')}.id"))
    height: Mapped[float] = mapped_column(Float)
    direction: Mapped[float] = mapped_column(Float)
    diameter: Mapped[float] = mapped_column(Float)

    project: Mapped[Project] = relationship(back_populates="sensor_positions")
    tree: Mapped[Tree] = relationship(back_populates="sensor_positions")
    sensor: Mapped[Sensor] = relationship(back_populates="sensor_position", uselist=False)
