"""Optional models describing tree crown bracing installations."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseEntity, table_name

if TYPE_CHECKING:  # pragma: no cover - imports for type checking only
    from .tree import Tree


class TreeCableType(BaseEntity):
    """Describe the type of a crown bracing installation."""

    __tablename__ = table_name("tree_cable_types")

    name: Mapped[str] = mapped_column(String, unique=True)
    cables: Mapped[list[TreeCable]] = relationship(back_populates="cable_type")


class TreeCable(BaseEntity):
    """Concrete crown bracing installed in a tree."""

    __tablename__ = table_name("tree_cables")

    tree_id: Mapped[int] = mapped_column(ForeignKey(f"{table_name('trees')}.id"))
    cable_type_id: Mapped[int] = mapped_column(ForeignKey(f"{table_name('tree_cable_types')}.id"))

    tree: Mapped[Tree] = relationship()
    cable_type: Mapped[TreeCableType] = relationship(back_populates="cables")


__all__ = ["TreeCableType", "TreeCable"]
