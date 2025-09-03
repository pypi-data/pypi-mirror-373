"""Database utilities for arbolab.

This package provides a thin abstraction over SQLAlchemy's session handling to
make database access convenient in interactive environments while remaining
fully compatible with more advanced use cases such as web applications.
"""

from .manager import DBManager
from .session import (
    current_session,
    make_session_factory,
    session_scope,
    with_session,
)

__all__ = [
    "DBManager",
    "make_session_factory",
    "session_scope",
    "current_session",
    "with_session",
]
