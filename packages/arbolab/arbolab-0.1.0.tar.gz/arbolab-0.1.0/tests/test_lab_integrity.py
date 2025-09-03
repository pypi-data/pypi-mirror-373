import pandas as pd
from pathlib import Path

from arbolab.config import Config
from arbolab.lab import Lab
from arbolab.classes.data import Data, DATA_DIR


def test_check_integrity_detects_inconsistencies(tmp_path, monkeypatch):
    monkeypatch.setenv("ARBOLAB_DATA_DIR", str(tmp_path / "data"))
    cfg = Config(working_dir=tmp_path)
    lab = Lab.setup(config=cfg, load_plugins=False, verify=False)

    df = pd.DataFrame({"a": [1]})
    data_obj = Data()
    data_obj.dataframe = df
    lab.db.create(data_obj)

    # Remove the stored file to create a missing file situation
    data_path = Path(data_obj.path)
    data_path.unlink()

    # Create an orphan file
    orphan = DATA_DIR / "orphan.parquet"
    df.to_parquet(orphan, engine="pyarrow", index=False)

    issues = lab.check_integrity()
    assert any("Missing data file" in msg for msg in issues)
    assert any("Orphan data file" in msg for msg in issues)

    lab.close(verify=False)
