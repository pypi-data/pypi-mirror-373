"""Helpers for working with data dictionary schema files.

The helpers in this module provide a lightweight way to describe the
structure of :class:`pandas.DataFrame` objects.  A *data dictionary* is a
JSON or YAML file containing a mapping of column names to their data
properties.  Each column definition requires a ``dtype`` and may optionally
include ``unit`` and ``description`` fields.

Example
-------
A data dictionary could look like this::

    {
        "columns": {
            "time": {"dtype": "float", "unit": "s", "description": "Seconds"},
            "value": {"dtype": "int"}
        }
    }

"""

from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path
from typing import NotRequired, Required, TypedDict

import pandas as pd
from pandas.api.types import (
    is_bool_dtype,
    is_float_dtype,
    is_integer_dtype,
    is_string_dtype,
)

try:  # pragma: no cover - optional dependency
    import yaml
except Exception:  # pragma: no cover - handled in ``load_data_dict``
    yaml = None


class ColumnSchema(TypedDict, total=False):
    """Schema information for a single DataFrame column."""

    dtype: Required[str]
    unit: NotRequired[str]
    description: NotRequired[str]


class DataDict(TypedDict):
    """Top level structure of a data dictionary."""

    columns: dict[str, ColumnSchema]


_TYPE_CHECKS: dict[str, Callable[[pd.Series], bool]] = {
    "bool": is_bool_dtype,
    "int": is_integer_dtype,
    "float": is_float_dtype,
    "str": is_string_dtype,
}


def load_data_dict(path: Path) -> DataDict:
    """Load a :class:`DataDict` from *path*.

    Parameters
    ----------
    path : :class:`~pathlib.Path`
        Location of the JSON or YAML file describing the data dictionary.

    Returns
    -------
    :class:`DataDict`
        Parsed data dictionary structure.

    Raises
    ------
    ValueError
        If the file format is not supported or the resulting structure is invalid.
    """

    suffix = path.suffix.lower()
    with path.open("r", encoding="utf8") as fh:
        if suffix == ".json":
            data = json.load(fh)
        elif suffix in {".yml", ".yaml"}:
            if yaml is None:
                raise ValueError("PyYAML is required to load YAML data dictionaries")
            data = yaml.safe_load(fh)
        else:  # pragma: no cover - defensive branch
            raise ValueError(f"Unsupported file extension: {suffix}")

    if not isinstance(data, dict) or "columns" not in data:
        raise ValueError("Data dictionary must contain a 'columns' mapping")

    return data  # type: ignore[return-value]


def validate_dataframe(df: pd.DataFrame, schema: DataDict) -> bool:
    """Validate that ``df`` matches *schema*.

    Parameters
    ----------
    df : :class:`pandas.DataFrame`
        The DataFrame to validate.
    schema : :class:`DataDict`
        Data dictionary schema describing required columns and their dtypes.

    Returns
    -------
    bool
        ``True`` if validation succeeds.

    Raises
    ------
    TypeError
        If ``df`` is not a DataFrame.
    ValueError
        If ``df`` violates the schema.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected a DataFrame, but got {type(df).__name__}")

    for col, spec in schema.get("columns", {}).items():
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

        dtype = spec["dtype"]
        check = _TYPE_CHECKS.get(dtype)
        if check is None:
            raise ValueError(f"Unsupported dtype '{dtype}' for column '{col}'")

        series = df[col]
        if not check(series):
            raise ValueError(f"Column '{col}' expected dtype '{dtype}', got '{series.dtype}'")

        if series.isnull().any():
            raise ValueError(f"Column '{col}' contains missing values")

    return True


__all__ = ["DataDict", "load_data_dict", "validate_dataframe"]
