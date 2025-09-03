import pandas as pd
import pytest

from arbolab.utils import (
    calc_amplitude,
    calc_min_max,
    calc_sample_rate,
    time_cut_by_datetime_index,
    validate_df,
    validate_time_format,
)


def test_calc_sample_rate_datetime_index() -> None:
    idx = pd.date_range("2023-01-01", periods=4, freq="1s")
    df = pd.DataFrame({"value": [1, 2, 3, 4]}, index=idx)
    assert calc_sample_rate(df) == pytest.approx(1.0)


def test_calc_sample_rate_time_column() -> None:
    df = pd.DataFrame({"time": [0.0, 0.5, 1.0], "val": [0, 1, 2]})
    assert calc_sample_rate(df, "time") == pytest.approx(2.0)


def test_calc_amplitude_and_min_max() -> None:
    df = pd.DataFrame({"t": [0, 1, 2], "s": [1, 3, 2]})
    assert calc_amplitude(df, "s") == 1.0
    result = calc_min_max(df, "s", "t")
    assert result["max"]["value"] == 3
    assert result["max"]["time"] == 1
    assert result["min"]["value"] == 1
    assert result["min"]["time"] == 0


def test_validate_time_format_and_cut() -> None:
    df = pd.DataFrame(
        {"a": [1, 2, 3]},
        index=pd.date_range("2024-01-01 00:00:00", periods=3, freq="1s"),
    )
    start = "2024-01-01 00:00:01"
    end = "2024-01-01 00:00:02"
    limited = time_cut_by_datetime_index(df, start, end)
    assert len(limited) == 2
    formatted = validate_time_format(start)
    assert formatted == "2024-01-01 00:00:01.000000"


def test_validate_df() -> None:
    df = pd.DataFrame({"a": [1, 2], "b": [3, 4]})
    assert validate_df(df, ["a"])
    with pytest.raises(TypeError):
        validate_df([1, 2])  # type: ignore[arg-type]
    with pytest.raises(ValueError):
        validate_df(pd.DataFrame(), ["a"])
    with pytest.raises(ValueError):
        validate_df(pd.DataFrame({"a": [1, None]}))
    with pytest.raises(ValueError):
        validate_df(df, ["c"])
