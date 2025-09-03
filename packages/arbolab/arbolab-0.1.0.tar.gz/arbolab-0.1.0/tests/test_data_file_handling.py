import pandas as pd
import pytest

from arbolab.classes.data import Data


def test_data_invalid_format(tmp_path, monkeypatch):
    monkeypatch.setenv("ARBOLAB_DATA_DIR", str(tmp_path))
    data = Data(format="csv")
    df = pd.DataFrame({"a": [1]})
    with pytest.raises(ValueError, match="Unsupported data format"):
        data.dataframe = df
    data.path = str(tmp_path / "dummy.csv")
    with pytest.raises(ValueError, match="Unsupported data format"):
        _ = data.dataframe


def test_data_missing_file(tmp_path, monkeypatch):
    monkeypatch.setenv("ARBOLAB_DATA_DIR", str(tmp_path))
    data = Data(path=str(tmp_path / "missing.parquet"))
    with pytest.raises(FileNotFoundError):
        _ = data.dataframe
