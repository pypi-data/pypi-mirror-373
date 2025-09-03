"""Database model representing a project within a lab."""

from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey, String, UniqueConstraint, select
from sqlalchemy.orm import Mapped, Session, mapped_column, relationship

from ..db import with_session
from .base import BaseEntity, table_name
from .lab_entry import LabEntry

if TYPE_CHECKING:  # pragma: no cover - for type checking only
    from ..lab import Lab as LabContainer
    from .measurement import Measurement
    from .sensor import Sensor
    from .sensor_position import SensorPosition
    from .series import Series
    from .tree import Tree


class Project(BaseEntity):
    """Project within a lab."""

    __tablename__ = table_name("projects")

    __table_args__ = (UniqueConstraint("lab_id", "name"),)

    lab_id: Mapped[int] = mapped_column(ForeignKey(f"{table_name('labs')}.id"))
    name: Mapped[str] = mapped_column(String)

    lab: Mapped[LabEntry] = relationship(back_populates="projects")
    series: Mapped[list[Series]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    sensors: Mapped[list[Sensor]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    sensor_positions: Mapped[list[SensorPosition]] = relationship(
        back_populates="project", cascade="all, delete-orphan"
    )
    trees: Mapped[list[Tree]] = relationship(back_populates="project", cascade="all, delete-orphan")
    measurements: Mapped[list[Measurement]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
        overlaps="sensor,series",
    )

    @classmethod
    @with_session
    def setup(cls, lab: LabContainer, name: str, *, session: Session) -> Project:
        """Create or load a project entry in the database.

        Running ``setup`` multiple times with the same ``lab`` and ``name``
        previously raised a ``IntegrityError`` due to the unique constraint on
        ``(lab_id, name)``. To make repeated invocations safe and idempotent,
        this method now checks for an existing project before creating a new
        one. If a matching project is found, it is returned as-is; otherwise a
        new project is created and committed.
        """
        db_lab = cls._default_lab(session)
        project = session.scalar(select(cls).where(cls.lab_id == db_lab.id, cls.name == name))
        if project is None:
            project = cls(name=name, lab_id=db_lab.id)
            session.add(project)
            session.commit()
        else:
            logging.warning("Project %s already exists, loading existing project", name)
        return project

    @classmethod
    @with_session
    def load(cls, lab: LabContainer, name: str, *, session: Session) -> Project:
        """Load an existing project by name."""
        project = session.scalar(select(cls).where(cls.name == name))
        if project is None:
            raise ValueError(f"Project {name!r} not found")
        return project

    @staticmethod
    def _default_lab(sess: Session) -> LabEntry:
        """Return the default lab entry, creating it if necessary."""
        db_lab = sess.scalar(select(LabEntry).limit(1))
        if db_lab is None:
            db_lab = LabEntry(name="default")
            sess.add(db_lab)
            sess.flush()
        return db_lab
