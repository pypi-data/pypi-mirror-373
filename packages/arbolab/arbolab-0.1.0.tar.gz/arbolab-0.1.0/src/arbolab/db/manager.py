"""Database manager using SQLAlchemy and DuckDB."""

from __future__ import annotations

from collections.abc import Mapping
from contextlib import AbstractContextManager
from typing import Any, TypeVar

from sqlalchemy.orm import Session, sessionmaker

# Import all ORM models so SQLAlchemy's metadata is fully populated before
# creating tables. Without this import, ``Base.metadata.create_all`` may miss
# some model definitions.
import arbolab.classes  # noqa: F401

from ..classes import Base, BaseEntity
from ..classes.status import Status
from ..config import DBConfig
from .session import make_engine_and_sessionmaker, session_scope

T = TypeVar("T", bound=BaseEntity)


class DBManager:
    """Manage database engine and sessions."""

    def __init__(self, url: str, config: DBConfig | None = None) -> None:
        self.url = url
        self.config = config or DBConfig()
        self.engine, self._sessionmaker = make_engine_and_sessionmaker(url, self.config)

    def ensure_meta(self) -> None:
        """Create tables if they do not yet exist."""
        Base.metadata.create_all(self.engine)

    def session(self) -> Session:
        """Return a new SQLAlchemy session."""
        return self._sessionmaker()

    @property
    def session_factory(self) -> sessionmaker:
        """Expose the underlying :class:`~sqlalchemy.orm.sessionmaker`."""
        return self._sessionmaker

    def session_scope(self, session: Session | None = None) -> AbstractContextManager[Session]:
        """Context manager that manages sessions using context variables."""
        return session_scope(self._sessionmaker, session=session)

    def create(self, obj: T, session: Session | None = None) -> T:
        """Persist *obj* and return it.

        Parameters
        ----------
        obj:
            Instance of a SQLAlchemy model to be stored.
        session:
            Optional session to use. If omitted a new session is managed
            automatically.
        """

        with self.session_scope(session) as sess:
            sess.add(obj)
            sess.flush()
        return obj

    def read(
        self,
        model: type[T],
        obj_id: object,
        session: Session | None = None,
        *,
        load_relations: bool = True,
    ) -> T:
        """Load *model* instance by primary key.

        When ``load_relations`` is ``True`` all relationships are eagerly
        loaded so the returned object can be used after the session is closed.

        Raises
        ------
        ValueError
            If no matching instance exists.
        """

        with self.session_scope(session) as sess:
            inst = sess.get(model, obj_id)
            if inst is None:
                raise ValueError(f"{model.__name__} with id {obj_id} not found")
            if load_relations:
                for rel in model.__mapper__.relationships:
                    getattr(inst, rel.key)
            # Detach so it can be safely used outside the session.
            sess.expunge(inst)
            return inst

    def update(self, obj: T, changes: Mapping[str, Any], session: Session | None = None) -> T:
        """Apply *changes* to *obj* and persist them.

        ``changes`` is a mapping of attribute names to their new values.
        """

        with self.session_scope(session) as sess:
            for key, value in changes.items():
                setattr(obj, key, value)
            sess.add(obj)
            sess.flush()
        return obj

    def delete(self, obj: T, session: Session | None = None, *, hard: bool = False) -> None:
        """Delete *obj* either softly or permanently.

        Parameters
        ----------
        hard:
            When ``True`` the instance is removed from the database. Otherwise,
            if the object defines a ``status`` attribute, it is marked as
            :class:`~arbolab.classes.status.Status.DELETED`.
        """

        with self.session_scope(session) as sess:
            if not hard and hasattr(obj, "status"):
                obj.status = Status.DELETED
                sess.add(obj)
            else:
                sess.delete(obj)

    def __repr__(self) -> str:  # pragma: no cover - trivial
        """Return a representation including URL and configuration."""
        return f"DBManager(url={self.url!r}, config={self.config!r})"
