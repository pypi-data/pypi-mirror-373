"""Measurement entities and versioning support."""

from __future__ import annotations

from typing import TYPE_CHECKING

import pandas as pd
from pydantic import BaseModel, Field
from sqlalchemy import (
    Float,
    ForeignKey,
    ForeignKeyConstraint,
    Integer,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship, validates

from .base import BaseEntity, table_name
from .data import Data

if TYPE_CHECKING:  # pragma: no cover - imports for type checking only
    from .project import Project
    from .sensor import Sensor
    from .series import Series


class Measurement(BaseEntity):
    """Abstract measurement captured by a sensor within a series.

    The actual numeric values live in :class:`MeasurementVersion` entries which
    track revisions of the measurement. The first version typically contains the
    raw value as recorded by the sensor while subsequent versions may represent
    corrected or processed values.
    """

    __tablename__ = table_name("measurements")
    __table_args__ = (
        ForeignKeyConstraint(
            ["series_id", "project_id"],
            [f"{table_name('series')}.id", f"{table_name('series')}.project_id"],
        ),
        ForeignKeyConstraint(
            ["sensor_id", "project_id"],
            [f"{table_name('sensors')}.id", f"{table_name('sensors')}.project_id"],
        ),
    )

    project_id: Mapped[int] = mapped_column(ForeignKey(f"{table_name('projects')}.id"))
    series_id: Mapped[int] = mapped_column(Integer)
    sensor_id: Mapped[int] = mapped_column(Integer)
    # ``timestamp`` is considered intrinsic to the measurement itself and does
    # not change across versions. Any value adjustments are stored in
    # :class:`MeasurementVersion`.
    timestamp: Mapped[float] = mapped_column(Float)

    # Additional metadata describing the measurement. ``unit`` specifies the
    # physical unit of the data points (e.g. ``"m/s"``), ``sample_rate`` stores
    # the sampling frequency in Hertz and ``sensor_type`` can be used to record
    # the type of sensor that created the measurement independent of the
    # ``Sensor`` entity. All fields provide sensible defaults and are validated
    # via the ``MeasurementMeta`` Pydantic model defined below.
    unit: Mapped[str] = mapped_column(String, default="unknown", nullable=False)
    sample_rate: Mapped[float] = mapped_column(Float, default=1.0, nullable=False)
    sensor_type: Mapped[str] = mapped_column(String, default="generic", nullable=False)

    data_id: Mapped[int | None] = mapped_column(ForeignKey(f"{table_name('data')}.id"))

    project: Mapped[Project] = relationship(back_populates="measurements")
    series: Mapped[Series] = relationship(back_populates="measurements", overlaps="project")
    sensor: Mapped[Sensor] = relationship(back_populates="measurements", overlaps="project,series")
    _data: Mapped[Data | None] = relationship(
        cascade="all, delete-orphan", single_parent=True, lazy="joined"
    )
    versions: Mapped[list[MeasurementVersion]] = relationship(
        back_populates="measurement",
        cascade="all, delete-orphan",
        order_by="MeasurementVersion.version",
        lazy="selectin",
    )

    # ------------------------------------------------------------------
    class MeasurementMeta(BaseModel):
        """Validation model for measurement metadata."""

        unit: str = Field(default="unknown")
        sample_rate: float = Field(default=1.0, ge=0)
        sensor_type: str = Field(default="generic")

    @validates("unit", "sample_rate", "sensor_type")
    def _validate_meta(self, key: str, value: object) -> object:
        """Validate metadata fields using the :class:`MeasurementMeta` model."""
        validated = self.MeasurementMeta.model_validate({key: value})
        return getattr(validated, key)

    @property
    def latest(self) -> MeasurementVersion | None:
        """Return the most recent version of this measurement."""
        if not self.versions:
            return None
        return self.versions[-1]

    # ------------------------------------------------------------------
    @property
    def data(self) -> pd.DataFrame | None:
        """Return associated data as :class:`~pandas.DataFrame`."""
        return None if self._data is None else self._data.dataframe

    @data.setter
    def data(self, df: pd.DataFrame | None) -> None:
        if df is None:
            self._data = None
        else:
            if self._data is None:
                self._data = Data()
            self._data.dataframe = df


class MeasurementVersion(BaseEntity):
    """Concrete revision of a :class:`Measurement`."""

    __tablename__ = table_name("measurement_versions")
    __table_args__ = (UniqueConstraint("measurement_id", "version"),)

    measurement_id: Mapped[int] = mapped_column(ForeignKey(f"{table_name('measurements')}.id"))
    # A monotonically increasing version number starting at 1 for the raw value.
    version: Mapped[int] = mapped_column(Integer, default=1)
    data_id: Mapped[int | None] = mapped_column(ForeignKey(f"{table_name('data')}.id"))

    measurement: Mapped[Measurement] = relationship(back_populates="versions")
    _data: Mapped[Data | None] = relationship(
        cascade="all, delete-orphan", single_parent=True, lazy="joined"
    )

    # ------------------------------------------------------------------
    @property
    def data(self) -> pd.DataFrame | None:
        """Return the stored data as :class:`~pandas.DataFrame`."""
        return None if self._data is None else self._data.dataframe

    @data.setter
    def data(self, df: pd.DataFrame | None) -> None:
        if df is None:
            self._data = None
        else:
            if self._data is None:
                self._data = Data()
            self._data.dataframe = df
