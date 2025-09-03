"""Session management helpers using SQLAlchemy and ``ContextVar``."""

from __future__ import annotations

from collections.abc import Callable, Generator
from contextlib import contextmanager
from contextvars import ContextVar
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker

from ..config import DBConfig

__all__ = [
    "make_engine_and_sessionmaker",
    "make_session_factory",
    "session_scope",
    "current_session",
    "with_session",
]

# ``None`` is used as the default to signal the absence of a session.
_SESSION_CTX: ContextVar[Session | None] = ContextVar("arbolab_session", default=None)


def make_engine_and_sessionmaker(
    url: str, config: DBConfig | None = None
) -> tuple[Engine, sessionmaker]:
    """Return a configured engine and :class:`~sqlalchemy.orm.sessionmaker`.

    Parameters
    ----------
    url:
        Database connection URL.
    config:
        Optional :class:`~arbolab.config.DBConfig` instance with engine options.
    """

    cfg = config or DBConfig()
    engine = create_engine(url, echo=cfg.echo, **cfg.engine_kwargs)
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    return engine, factory


def make_session_factory(url: str, config: DBConfig | None = None) -> sessionmaker:
    """Return a configured :class:`~sqlalchemy.orm.sessionmaker`."""

    _, factory = make_engine_and_sessionmaker(url, config)
    return factory


def current_session() -> Session | None:
    """Return the session currently active in the context, if any."""

    return _SESSION_CTX.get()


@contextmanager
def session_scope(
    factory: sessionmaker, *, session: Session | None = None
) -> Generator[Session, None, None]:
    """Provide a transactional scope around a series of operations.

    If ``session`` is provided or a session already exists in the current
    :class:`~contextvars.ContextVar`, it is reused. Otherwise a new session is
    created using ``factory``. The session is committed if the context exits
    normally and rolled back on exception.
    """

    if session is not None:
        token = _SESSION_CTX.set(session)
        try:
            yield session
        finally:  # pragma: no cover - trivial cleanup
            _SESSION_CTX.reset(token)
        return

    existing = current_session()
    if existing is not None:
        # Reuse the session already present in the context.
        yield existing
        return

    sess = factory()
    token = _SESSION_CTX.set(sess)
    try:
        yield sess
        sess.commit()
    except Exception:  # pragma: no cover - error path
        sess.rollback()
        raise
    finally:  # pragma: no cover - ensure cleanup
        sess.close()
        _SESSION_CTX.reset(token)


def with_session[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    """Decorator injecting a SQLAlchemy session into ``func``.

    The decorated function must accept a ``session`` keyword argument. The
    decorator looks for an existing session in the context and only creates a
    new one when necessary. A session factory is inferred from the ``lab``
    argument (common for class or instance methods) or from ``self.db``.
    """

    @wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        # Explicitly provided session wins.
        sess: Session | None = kwargs.get("session") or current_session()
        if sess is not None:
            kwargs["session"] = sess
            return func(*args, **kwargs)

        # Try to locate a session factory from common argument patterns.
        lab = kwargs.get("lab")
        if lab is None and len(args) >= 1:
            obj = args[0]
            # ``obj`` might be ``cls`` for a classmethod or ``self`` for an
            # instance method. The lab may be the next positional argument or an
            # attribute of ``obj`` itself.
            if hasattr(obj, "db") and obj.db is not None:
                lab = obj
            elif len(args) >= 2:
                lab = args[1]
        if lab is None:
            raise RuntimeError("Session factory could not be inferred")

        # ``lab`` may either provide ``session_factory`` directly or have a
        # ``db`` attribute pointing to an object that does.
        factory = getattr(getattr(lab, "db", lab), "session_factory", None)
        if factory is None:
            raise RuntimeError("Object does not provide a session factory")

        with session_scope(factory) as sess2:
            kwargs["session"] = sess2
            return func(*args, **kwargs)

    return wrapper
