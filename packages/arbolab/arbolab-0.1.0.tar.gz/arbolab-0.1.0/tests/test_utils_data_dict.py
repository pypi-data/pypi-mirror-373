import json
from pathlib import Path

import pandas as pd
import pytest

from arbolab.utils import load_data_dict, validate_dataframe


def test_load_data_dict_json(tmp_path: Path) -> None:
    schema = {
        "columns": {
            "a": {"dtype": "int", "unit": "m"},
            "b": {"dtype": "float", "description": "values"},
        }
    }
    file = tmp_path / "schema.json"
    file.write_text(json.dumps(schema))
    loaded = load_data_dict(file)
    assert loaded == schema


def test_load_data_dict_yaml(tmp_path: Path) -> None:
    schema = {"columns": {"c": {"dtype": "str"}}}
    file = tmp_path / "schema.yaml"
    file.write_text("""
columns:
  c:
    dtype: str
""")
    loaded = load_data_dict(file)
    assert loaded == schema


def test_validate_dataframe_pass() -> None:
    schema = {"columns": {"a": {"dtype": "int"}, "b": {"dtype": "float"}}}
    df = pd.DataFrame({"a": [1, 2], "b": [0.1, 0.2]})
    assert validate_dataframe(df, schema)


def test_validate_dataframe_failures() -> None:
    schema = {"columns": {"a": {"dtype": "int"}}}
    df_missing = pd.DataFrame({"b": [1]})
    with pytest.raises(ValueError):
        validate_dataframe(df_missing, schema)

    df_wrong = pd.DataFrame({"a": ["x"]})
    with pytest.raises(ValueError):
        validate_dataframe(df_wrong, schema)
