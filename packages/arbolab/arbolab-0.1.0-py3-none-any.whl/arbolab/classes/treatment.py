"""Optional database models describing treatments applied to project entities."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseEntity, table_name

if TYPE_CHECKING:  # pragma: no cover - imports for type checking only
    from .tree import Tree


class TreatmentType(BaseEntity):
    """General description of a treatment variant."""

    __tablename__ = table_name("treatment_types")

    name: Mapped[str] = mapped_column(String, unique=True)
    treatments: Mapped[list[Treatment]] = relationship(back_populates="treatment_type")


class Treatment(BaseEntity):
    """Concrete application of a treatment to an entity."""

    __tablename__ = table_name("treatments")

    treatment_type_id: Mapped[int] = mapped_column(
        ForeignKey(f"{table_name('treatment_types')}.id")
    )
    tree_id: Mapped[int | None] = mapped_column(
        ForeignKey(f"{table_name('trees')}.id"), nullable=True
    )
    subject_type: Mapped[str | None] = mapped_column(String, nullable=True)
    subject_identifier: Mapped[str | None] = mapped_column(String, nullable=True)

    treatment_type: Mapped[TreatmentType] = relationship(back_populates="treatments")
    tree: Mapped[Tree | None] = relationship()


__all__ = ["TreatmentType", "Treatment"]
