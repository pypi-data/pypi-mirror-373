"""Utility helpers for working with pandas DataFrames.

This module contains small, well tested helpers that are shared across
multiple sensor packages.  They focus on generic DataFrame operations and
intentionally avoid sensor specific logic.
"""

from __future__ import annotations

import json
from collections.abc import Sequence
from datetime import datetime
from pathlib import Path

import numpy as np
import pandas as pd


def calc_sample_rate(data: pd.DataFrame | pd.Series, time_column: str | None = None) -> float:
    """Calculate the sample rate of *data* in Hertz.

    The function either uses the provided ``time_column`` with numeric time
    values in seconds or, if ``time_column`` is ``None``, expects a
    ``DatetimeIndex`` on the input.

    Parameters
    ----------
    data : Union[pandas.DataFrame, pandas.Series]
        Input data containing time information.
    time_column : str, optional
        Name of the column with time values in seconds.  If not given the
        index of ``data`` must be a ``DatetimeIndex``.

    Returns
    -------
    float
        Calculated sample rate in Hertz.

    Raises
    ------
    TypeError
        If ``data`` is not a pandas DataFrame or Series.
    ValueError
        If insufficient time information is available.
    """
    if not isinstance(data, pd.DataFrame | pd.Series):

        raise TypeError("data must be a pandas DataFrame or Series")

    if time_column is not None:
        if not isinstance(data, pd.DataFrame):
            raise TypeError("time_column can only be used with a DataFrame")
        if time_column not in data.columns:
            raise ValueError(f"Column '{time_column}' does not exist in the data")
        time_values = pd.to_numeric(data[time_column], errors="coerce")
        if time_values.isnull().any():
            raise ValueError("Time column contains non-numeric values")
        time_deltas = time_values.diff().dropna().to_numpy()
    else:
        if not isinstance(data.index, pd.DatetimeIndex):
            raise ValueError("Data must have a DatetimeIndex when time_column is None")
        time_deltas = data.index.to_series().diff().dt.total_seconds().dropna().to_numpy()

    if time_deltas.size == 0:
        raise ValueError("Cannot calculate sample rate from fewer than two samples")

    mean_delta = float(np.mean(time_deltas))
    if mean_delta <= 0:
        raise ValueError("Time values must be strictly increasing")

    return 1.0 / mean_delta


def calc_amplitude(df: pd.DataFrame, column_name: str) -> float:
    """Return half the peak-to-peak amplitude of ``column_name``.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the column of interest.
    column_name : str
        Name of the column for which to calculate the amplitude.

    Returns
    -------
    float
        Half the difference between the column's maximum and minimum value.

    Raises
    ------
        ValueError
        If ``column_name`` does not exist or the column contains no numeric data.
    """
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' does not exist in the DataFrame")

    series = pd.to_numeric(df[column_name], errors="coerce")
    if series.isnull().all():
        raise ValueError("Column contains no numeric data")

    amplitude = (series.max() - series.min()) / 2.0
    return float(amplitude)


def calc_min_max(
    df: pd.DataFrame, sensor_column: str, time_column: str
) -> dict[str, dict[str, object]]:
    """Return minimum and maximum information for ``sensor_column``.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame containing the sensor readings and corresponding time values.
    sensor_column : str
        Column with the sensor readings.
    time_column : str
        Column with time values used to report when min and max occurred.

    Returns
    -------
    dict of dict
        A dictionary with ``"max"`` and ``"min"`` entries.  Each entry contains
        ``idx`` (index label), ``time`` and ``value``.

    Raises
    ------
        ValueError
        If required columns are missing or contain no numeric data.
    """
    for col in (sensor_column, time_column):
        if col not in df.columns:
            raise ValueError(f"Column '{col}' does not exist in the DataFrame")

    series = pd.to_numeric(df[sensor_column], errors="coerce")
    if series.isnull().all():
        raise ValueError("Sensor column contains no numeric data")

    max_idx = series.idxmax()
    min_idx = series.idxmin()

    return {
        "max": {
            "idx": max_idx,
            "time": df.at[max_idx, time_column],
            "value": series.loc[max_idx],
        },
        "min": {
            "idx": min_idx,
            "time": df.at[min_idx, time_column],
            "value": series.loc[min_idx],
        },
    }


def validate_time_format(time_str: str, additional_formats: Sequence[str] | None = None) -> str:
    """Validate ``time_str`` and return it in ``"%Y-%m-%d %H:%M:%S.%f"`` format.

    Parameters
    ----------
    time_str : str
        The time string to validate and convert.
    additional_formats : sequence of str, optional
        Additional time formats to try for parsing.

    Returns
    -------
    str
        ``time_str`` converted to the target format.

    Raises
    ------
        ValueError
        If ``time_str`` does not match any known format.
    """
    target_format = "%Y-%m-%d %H:%M:%S.%f"
    formats = [
        "%Y-%m-%d %H:%M:%S.%f",
        "%Y-%m-%d %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S",
        "%Y-%m-%dT%H:%M:%S.%f",
    ]
    if additional_formats:
        formats.extend(additional_formats)

    for fmt in formats:
        try:
            parsed = datetime.strptime(time_str, fmt)
            return parsed.strftime(target_format)
        except ValueError:
            continue

    raise ValueError(f"Time string '{time_str}' does not match any known formats")


def time_cut_by_datetime_index(data: pd.DataFrame, start_time: str, end_time: str) -> pd.DataFrame:
    """Return ``data`` limited to the range ``start_time`` – ``end_time``.

    Parameters
    ----------
    data : pandas.DataFrame
        Data with a ``DatetimeIndex``.
    start_time : str
        Inclusive start time.
    end_time : str
        Inclusive end time.

    Returns
    -------
    pandas.DataFrame
        The sliced DataFrame.

    Raises
    ------
        ValueError
        If ``data`` does not have a ``DatetimeIndex``.
    """
    if not isinstance(data.index, pd.DatetimeIndex):
        raise ValueError("DataFrame index must be of type DatetimeIndex")

    start = pd.to_datetime(start_time)
    end = pd.to_datetime(end_time)
    return data.loc[start:end]


def validate_df(df: pd.DataFrame, columns: Sequence[str] | None = None) -> bool:
    """Validate basic properties of ``df``.

    Parameters
    ----------
    df : pandas.DataFrame
        DataFrame to validate.
    columns : sequence of str, optional
        Required column names.  Additional columns are permitted.

    Returns
    -------
    bool
        ``True`` if validation passes.

    Raises
    ------
    TypeError
        If ``df`` is not a DataFrame.
        ValueError
        If ``df`` is empty, missing required columns or contains missing values.
    """
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected a DataFrame, but got {type(df).__name__}")

    if df.empty:
        raise ValueError("The DataFrame has no rows")

    subset = df
    if columns is not None:
        missing_cols = [col for col in columns if col not in df.columns]
        if missing_cols:
            raise ValueError(f"The DataFrame is missing the following columns: {missing_cols}")
        subset = df[columns]

    if subset.isnull().any().any():
        raise ValueError("The DataFrame contains missing values")

    return True


def validate_dataframe(df: pd.DataFrame, schema_path: str | Path) -> bool:
    """Validate ``df`` against a schema described in ``schema_path``.

    The schema is expected to be a JSON mapping of column names to dtype
    strings as returned by :attr:`pandas.Series.dtype`.

    Parameters
    ----------
    df:
        DataFrame to validate.
    schema_path:
        Path to a JSON file describing the expected schema.

    Returns
    -------
    bool
        ``True`` if validation passes.

    Raises
    ------
    ValueError
        If columns do not match the schema.
    TypeError
        If a column dtype does not match the schema.
    """

    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"Expected a DataFrame, but got {type(df).__name__}")

    with Path(schema_path).open("r", encoding="utf-8") as f:
        schema: dict[str, str] = json.load(f)

    expected_cols = list(schema.keys())
    missing = [col for col in expected_cols if col not in df.columns]
    unexpected = [col for col in df.columns if col not in expected_cols]
    if missing or unexpected:
        raise ValueError(
            "DataFrame columns do not match schema. "
            f"Missing: {missing}, unexpected: {unexpected}"
        )

    for col, expected_dtype in schema.items():
        actual_dtype = str(df[col].dtype)
        if actual_dtype != expected_dtype:
            raise TypeError(
                f"Column '{col}' has dtype '{actual_dtype}' but expected '{expected_dtype}'"
            )

    return True


__all__ = [
    "calc_sample_rate",
    "calc_amplitude",
    "calc_min_max",
    "validate_time_format",
    "time_cut_by_datetime_index",
    "validate_df",
    "validate_dataframe",
]
