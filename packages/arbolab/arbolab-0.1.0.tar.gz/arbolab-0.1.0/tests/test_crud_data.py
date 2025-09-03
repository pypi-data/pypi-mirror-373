import json
import pandas as pd
import pytest
from pathlib import Path

from arbolab.lab import Lab
from arbolab.config import Config


def test_crud_data(tmp_path, monkeypatch):
    monkeypatch.setenv("ARBOLAB_DATA_DIR", str(tmp_path / "data"))
    from arbolab.classes.data import Data, Status

    lab = Lab.setup(Config(working_dir=tmp_path), load_plugins=False)

    df = pd.DataFrame({"value": [1]})
    data = Data()
    data.dataframe = df
    lab.db.create(data)
    file_path = Path(data.path)
    assert file_path.exists()

    loaded = lab.db.read(Data, data.id)
    assert loaded.dataframe.equals(df)

    new_df = pd.DataFrame({"value": [2]})
    lab.db.update(loaded, {"dataframe": new_df})
    reloaded = lab.db.read(Data, data.id)
    assert reloaded.dataframe.loc[0, "value"] == 2

    lab.db.delete(reloaded)
    soft = lab.db.read(Data, data.id)
    assert soft.status is Status.DELETED
    assert Path(soft.path).exists()

    lab.db.delete(soft, hard=True)
    with pytest.raises(ValueError):
        lab.db.read(Data, data.id)
    assert not file_path.exists()


def test_dataframe_validation(tmp_path, monkeypatch):
    monkeypatch.setenv("ARBOLAB_DATA_DIR", str(tmp_path / "data"))
    from arbolab.classes.data import Data

    lab = Lab.setup(Config(working_dir=tmp_path), load_plugins=False)

    schema_file = tmp_path / "schema.json"
    schema_file.write_text(json.dumps({"value": "int64"}))

    valid = Data(schema_path=str(schema_file))
    valid_df = pd.DataFrame({"value": pd.Series([1], dtype="int64")})
    valid.dataframe = valid_df
    lab.db.create(valid)

    invalid_col = Data(schema_path=str(schema_file))
    with pytest.raises(ValueError):
        invalid_col.dataframe = pd.DataFrame({"wrong": [1]})

    invalid_dtype = Data(schema_path=str(schema_file))
    with pytest.raises(TypeError):
        invalid_dtype.dataframe = pd.DataFrame({"value": pd.Series([1.0], dtype="float64")})
