import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from arbolab.config import Config
from arbolab.lab import Lab
from arbolab.db.session import session_scope, current_session, with_session


def test_session_scope_commit_and_rollback(tmp_path):
    lab = Lab.setup(Config(working_dir=tmp_path), load_plugins=False)
    factory = lab.db.session_factory

    # create table
    with session_scope(factory) as sess:
        sess.execute(text("CREATE TABLE test (id INTEGER)"))

    # commit
    with session_scope(factory) as sess:
        sess.execute(text("INSERT INTO test VALUES (1)"))

    with session_scope(factory) as sess:
        assert current_session() is sess
        count = sess.execute(text("SELECT COUNT(*) FROM test")).scalar()
    assert count == 1

    # rollback
    with pytest.raises(RuntimeError):
        with session_scope(factory) as sess:
            sess.execute(text("INSERT INTO test VALUES (2)"))
            raise RuntimeError("boom")

    with session_scope(factory) as sess:
        count = sess.execute(text("SELECT COUNT(*) FROM test")).scalar()
    assert count == 1

    # reuse existing session
    with session_scope(factory) as sess1:
        with session_scope(factory) as sess2:
            assert sess1 is sess2


def test_with_session_reuse_and_create(tmp_path):
    lab = Lab.setup(Config(working_dir=tmp_path), load_plugins=False)

    @with_session
    def get_session(lab=None, *, session):
        session.execute(text("SELECT 1"))
        return session

    with lab.db.session_scope() as sess:
        assert get_session(lab, session=sess) is sess

    with lab.db.session_scope() as sess:
        assert get_session(lab) is sess

    new_session = get_session(lab)
    assert isinstance(new_session, Session)
    new_session.close()
