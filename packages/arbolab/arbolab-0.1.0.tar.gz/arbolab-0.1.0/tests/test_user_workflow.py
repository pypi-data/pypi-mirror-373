from pathlib import Path

from arbolab import Config, setup, Project
from arbolab.classes.tree import Tree


def test_user_can_create_lab_project_and_tree(tmp_path: Path) -> None:
    """Simulate basic user workflow creating lab, project and tree."""
    lab = setup(Config(working_dir=tmp_path), load_plugins=False)
    project = Project.setup(lab, "demo")
    with lab.db.session() as sess:
        tree = Tree(name="oak", project=project)
        sess.add(tree)
        sess.commit()
        saved = sess.get(Tree, tree.id)
        assert saved is not None
        assert saved.name == "oak"
        assert saved.project_id == project.id
