"""Database model describing a sensor type."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseEntity, table_name

if TYPE_CHECKING:  # pragma: no cover - imports for type checking only
    from .sensor import Sensor


class SensorType(BaseEntity):
    """Sensor type definition."""

    __tablename__ = table_name("sensor_types")
    __table_args__ = (UniqueConstraint("name"),)

    name: Mapped[str] = mapped_column(String, unique=True)

    sensors: Mapped[list[Sensor]] = relationship(back_populates="sensor_type")
