from pathlib import Path

import pandas as pd
import pytest
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError, InvalidRequestError

from arbolab.classes.measurement import Measurement, MeasurementVersion
from arbolab.classes.project import Project
from arbolab.classes.sensor import Sensor
from arbolab.classes.sensor_position import SensorPosition
from arbolab.classes.sensor_type import SensorType
from arbolab.classes.series import Series
from arbolab.classes.tree import Tree
from arbolab.config import Config
from arbolab.lab import Lab


def test_measurement_versions(tmp_path: Path) -> None:
    lab = Lab.setup(Config(working_dir=tmp_path), load_plugins=False)
    project = Project.setup(lab, "demo")

    with lab.db.session() as sess:
        tree = Tree(name="oak", project=project)
        series = Series(name="s1", project=project)
        stype = SensorType(name="generic")
        spos = SensorPosition(project=project, tree=tree, height=1.0, direction=0.0, diameter=0.1)
        sensor = Sensor(
            name="sens",
            project=project,
            tree=tree,
            sensor_type=stype,
            sensor_position=spos,
        )
        meas = Measurement(
            series=series,
            sensor=sensor,
            project=project,
            timestamp=0.0,
            unit="m/s",
            sample_rate=1.0,
            sensor_type="generic",
        )
        v1 = MeasurementVersion(version=1)
        v1.data = pd.DataFrame({"value": [10.0]})
        v2 = MeasurementVersion(version=2)
        v2.data = pd.DataFrame({"value": [11.0]})
        meas.versions.extend([v1, v2])
        sess.add(meas)
        sess.commit()

        saved = sess.scalar(select(Measurement).where(Measurement.id == meas.id))
        assert saved is not None
        assert len(saved.versions) == 2
        assert saved.unit == "m/s"
        assert saved.sample_rate == 1.0
        assert saved.sensor_type == "generic"
        assert saved.latest is not None
        latest_df = saved.latest.data
        assert latest_df is not None
        assert latest_df.loc[0, "value"] == 11.0


def test_measurement_project_consistency(tmp_path: Path) -> None:
    lab = Lab.setup(Config(working_dir=tmp_path), load_plugins=False)
    project1 = Project.setup(lab, "p1")
    project2 = Project.setup(lab, "p2")

    with lab.db.session() as sess:
        project1 = sess.get(Project, project1.id)
        project2 = sess.get(Project, project2.id)
        tree1 = Tree(name="t1", project=project1)
        tree2 = Tree(name="t2", project=project2)
        series = Series(name="s1", project=project1)
        stype = SensorType(name="generic")
        spos = SensorPosition(project=project2, tree=tree2, height=1.0, direction=0.0, diameter=0.1)
        sensor = Sensor(
            name="sens",
            project=project2,
            tree=tree2,
            sensor_type=stype,
            sensor_position=spos,
        )
        meas = Measurement(
            series=series,
            sensor=sensor,
            project=project1,
            timestamp=0.0,
            unit="m/s",
            sample_rate=1.0,
            sensor_type="generic",
        )
        with pytest.raises((IntegrityError, InvalidRequestError)):
            sess.add_all([meas, tree1, tree2, series, sensor])
            sess.commit()
