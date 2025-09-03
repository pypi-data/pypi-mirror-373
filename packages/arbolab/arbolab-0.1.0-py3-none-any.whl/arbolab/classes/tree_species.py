"""Database model representing a tree species."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import BaseEntity, table_name

if TYPE_CHECKING:  # pragma: no cover - imports for type checking only
    from .tree import Tree


class TreeSpecies(BaseEntity):
    """Represent a tree species."""

    __tablename__ = table_name("tree_species")

    name: Mapped[str] = mapped_column(String, unique=True)

    trees: Mapped[list[Tree]] = relationship(back_populates="tree_species")
