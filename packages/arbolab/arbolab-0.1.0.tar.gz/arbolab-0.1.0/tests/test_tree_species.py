import math
from pathlib import Path

import pytest

from arbolab import Config, Project, setup
from arbolab.classes.tree import Tree
from arbolab.classes.tree_species import TreeSpecies


def test_tree_diameter_and_species(tmp_path: Path) -> None:
    lab = setup(Config(working_dir=tmp_path), load_plugins=False)
    project = Project.setup(lab, "demo")
    with lab.db.session() as sess:
        species = TreeSpecies(name="oak")
        tree = Tree(
            name="oak1",
            project=project,
            circumference=math.pi * 10,
            tree_species=species,
        )
        sess.add_all([species, tree])
        sess.commit()
        saved = sess.get(Tree, tree.id)
        assert saved is not None
        assert saved.diameter == pytest.approx(10.0)
        assert saved.tree_species is not None
        assert saved.tree_species.name == "oak"
