import pandas as pd

from arbolab.config import Config
from arbolab.lab import Lab
from arbolab.classes import Project, Series, Tree
from arbolab_wind.processing import build_sensor, generate_measurements, to_measurements


def test_to_measurements(tmp_path):
    lab = Lab.setup(Config(working_dir=tmp_path), load_plugins=False)
    project = Project.setup(lab, "demo")

    with lab.db.session() as sess:
        project = sess.get(Project, project.id)
        tree = Tree(name="oak", project=project)
        series = Series(name="wind", project=project)
        df = pd.DataFrame({"speed": [1.0, 2.0]}, index=[0.0, 1.0])
        meta = {
            "sensor_type": "anemometer",
            "sensor_name": "a1",
            "unit": "m/s",
            "sample_rate": 1.0,
            "tree": tree,
            "height": 1.0,
            "direction": 0.0,
            "diameter": 0.1,
            "series": series,
        }
        measurements = to_measurements(df, meta, project, sensor=None)
        assert len(measurements) == 2
        m0 = measurements[0]
        assert m0.sensor.sensor_type.name == "anemometer"
        assert m0.unit == "m/s"
        assert m0.sample_rate == 1.0
        assert m0.sensor_type == "anemometer"
        version = m0.versions[0]
        pending = getattr(version._data, "_pending_path", None)
        assert pending is not None
        df_loaded = pd.read_parquet(pending, engine="pyarrow")
        assert df_loaded.loc[0, "speed"] == 1.0


def test_build_sensor(tmp_path):
    lab = Lab.setup(Config(working_dir=tmp_path), load_plugins=False)
    project = Project.setup(lab, "demo")

    with lab.db.session() as sess:
        project = sess.get(Project, project.id)
        tree = Tree(name="oak", project=project)
        meta = {
            "sensor_type": "anemometer",
            "sensor_name": "a1",
            "tree": tree,
            "height": 1.0,
            "direction": 0.0,
            "diameter": 0.1,
        }
        sensor = build_sensor(meta, project)
        assert sensor.sensor_type.name == "anemometer"
        assert sensor.sensor_position.height == 1.0
        assert sensor.name == "a1"


def test_generate_measurements(tmp_path):
    lab = Lab.setup(Config(working_dir=tmp_path), load_plugins=False)
    project = Project.setup(lab, "demo")

    with lab.db.session() as sess:
        project = sess.get(Project, project.id)
        tree = Tree(name="oak", project=project)
        series = Series(name="wind", project=project)
        df = pd.DataFrame({"speed": [1.0, 2.0]}, index=[0.0, 1.0])
        meta = {
            "sensor_type": "anemometer",
            "sensor_name": "a1",
            "unit": "m/s",
            "sample_rate": 1.0,
            "tree": tree,
            "height": 1.0,
            "direction": 0.0,
            "diameter": 0.1,
            "series": series,
        }
        sensor = build_sensor(meta, project)
        measurements = list(generate_measurements(df, meta, project, sensor))
        assert len(measurements) == 2
        m0 = measurements[0]
        assert m0.sensor.sensor_type.name == "anemometer"
        assert m0.unit == "m/s"
        assert m0.sample_rate == 1.0
