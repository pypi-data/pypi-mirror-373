"""Database model for laboratories and their projects."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseEntity, table_name

if TYPE_CHECKING:  # pragma: no cover - typing only
    from .project import Project


class LabEntry(BaseEntity):
    """Database record representing a laboratory with its projects."""

    __tablename__ = table_name("labs")

    name: Mapped[str] = mapped_column(String, unique=True)

    projects: Mapped[list[Project]] = relationship(
        back_populates="lab", cascade="all, delete-orphan"
    )
