"""Database model describing a physical sensor."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseEntity, table_name

if TYPE_CHECKING:  # pragma: no cover - imports for type checking only
    from .measurement import Measurement
    from .project import Project
    from .sensor_position import SensorPosition
    from .sensor_type import SensorType
    from .tree import Tree


class Sensor(BaseEntity):
    """Sensor definition."""

    __tablename__ = table_name("sensors")

    __table_args__ = (
        UniqueConstraint("project_id", "name"),
        UniqueConstraint("id", "project_id"),
    )

    project_id: Mapped[int] = mapped_column(ForeignKey(f"{table_name('projects')}.id"))
    tree_id: Mapped[int] = mapped_column(ForeignKey(f"{table_name('trees')}.id"), nullable=False)
    name: Mapped[str] = mapped_column(String)
    sensor_type_id: Mapped[int] = mapped_column(ForeignKey(f"{table_name('sensor_types')}.id"))
    sensor_position_id: Mapped[int] = mapped_column(
        ForeignKey(f"{table_name('sensor_positions')}.id")
    )

    project: Mapped[Project] = relationship(back_populates="sensors")
    tree: Mapped[Tree] = relationship(back_populates="sensors")
    sensor_type: Mapped[SensorType] = relationship(back_populates="sensors")
    sensor_position: Mapped[SensorPosition] = relationship(back_populates="sensor")
    measurements: Mapped[list[Measurement]] = relationship(
        back_populates="sensor",
        cascade="all, delete-orphan",
        overlaps="project,series,measurements",
    )
