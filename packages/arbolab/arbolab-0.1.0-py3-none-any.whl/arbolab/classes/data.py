"""Data container storing large measurement data outside the database."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Literal
from uuid import uuid4

import pandas as pd
from sqlalchemy import Enum, String, event
from sqlalchemy.engine import Connection
from sqlalchemy.orm import Mapped, Mapper, Session, mapped_column, object_session

from ..utils import load_data_dict, validate_dataframe
from .base import BaseEntity, table_name
from .status import Status

# Directory where data files are stored. Can be overridden via environment.
DATA_DIR = Path(os.getenv("ARBOLAB_DATA_DIR", "data")).resolve()
DATA_DIR.mkdir(parents=True, exist_ok=True)


class Data(BaseEntity):
    """Persist a ``pandas.DataFrame`` in an external file.

    The actual binary data is stored in a parquet or feather file on disk. Only
    the file path and format are stored in the database. Users interact with the
    data via the :pyattr:`dataframe` attribute which transparently loads and
    stores the underlying file.
    """

    __tablename__ = table_name("data")

    path: Mapped[str] = mapped_column(String, nullable=False)
    format: Mapped[Literal["parquet", "feather"] | None] = mapped_column(
        String(10), default="parquet"
    )
    schema_path: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[Status] = mapped_column(Enum(Status), default=Status.ACTIVE, nullable=False)

    # ------------------------------------------------------------------
    def _normalise_format(self) -> str:
        """Return the serialisation format or raise if unsupported."""
        fmt = self.format or "parquet"
        if fmt not in {"parquet", "feather"}:
            raise ValueError(f"Unsupported data format: {fmt}")
        return fmt

    # ------------------------------------------------------------------
    def _ensure_path(self) -> Path:
        """Create a file path for new data if necessary."""
        fmt = self._normalise_format()
        if not self.path:
            ext = "parquet" if fmt == "parquet" else "feather"
            self.path = str(DATA_DIR / f"{uuid4()}.{ext}")
        return Path(self.path)

    # ------------------------------------------------------------------
    @property
    def dataframe(self) -> pd.DataFrame:
        """Return the stored data as :class:`~pandas.DataFrame`."""
        path = Path(self.path)
        fmt = self._normalise_format()
        if not path.exists():
            pending_attr = getattr(self, "_pending_path", None)
            if pending_attr is not None:
                pending = Path(pending_attr)
                if pending.exists():
                    path = pending
                else:
                    raise FileNotFoundError(path)
            else:
                raise FileNotFoundError(path)
        if fmt == "parquet":
            return pd.read_parquet(path, engine="pyarrow")
        return pd.read_feather(path)

    @dataframe.setter
    def dataframe(self, df: pd.DataFrame) -> None:
        """Persist ``df`` to a temporary file and queue it for commit."""
        if self.schema_path:
            path = Path(self.schema_path)
            try:
                schema = load_data_dict(path)
            except ValueError:
                with path.open("r", encoding="utf8") as fh:
                    data = json.load(fh)
                columns = {}
                for key, dtype in data.items():
                    dtype_str = str(dtype)
                    if dtype_str.startswith("int"):
                        dtype_str = "int"
                    elif dtype_str.startswith("float"):
                        dtype_str = "float"
                    elif dtype_str.startswith("str"):
                        dtype_str = "str"
                    elif dtype_str.startswith("bool"):
                        dtype_str = "bool"
                    columns[key] = {"dtype": dtype_str}
                schema = {"columns": columns}
            try:
                validate_dataframe(df, schema)
            except ValueError as exc:
                msg = str(exc)
                if msg.startswith("Column") and "expected dtype" in msg:
                    raise TypeError(msg) from exc
                raise

        path = self._ensure_path()
        fmt = self._normalise_format()

        # Write to a temporary file first so rollbacks can be handled cleanly.
        tmp = path.with_suffix(path.suffix + ".tmp")
        if fmt == "parquet":
            df.to_parquet(tmp, engine="pyarrow", index=False)
        else:
            df.to_feather(tmp)

        # Mark the temporary file to be finalized after commit.
        self._pending_path = str(tmp)

    # ------------------------------------------------------------------
    def delete_file(self) -> None:
        """Remove the underlying file if it exists."""
        path = Path(self.path)
        if path.exists():
            path.unlink()


@event.listens_for(Data, "before_delete")
def _queue_file_removal(mapper: Mapper[Data], connection: Connection, target: Data) -> None:
    """Remember files slated for deletion until the transaction commits."""
    sess = object_session(target)
    if sess is not None:
        sess.info.setdefault("deleted_data_paths", []).append(target.path)


@event.listens_for(Session, "after_commit")
def _finalize_data_files(session: Session) -> None:  # pragma: no cover - filesystem
    """Finalize pending data file operations after a commit."""
    # Finalize newly written files
    for obj in session.identity_map.values():
        if isinstance(obj, Data):
            pending = getattr(obj, "_pending_path", None)
            if pending is not None:
                Path(pending).replace(Path(obj.path))
                delattr(obj, "_pending_path")

    # Remove files queued for deletion
    for path in session.info.pop("deleted_data_paths", []):
        Path(path).unlink(missing_ok=True)


@event.listens_for(Session, "after_rollback")
def _cleanup_pending_files(session: Session) -> None:  # pragma: no cover - filesystem
    """Clean up temporary files if the transaction rolls back."""
    for obj in session.identity_map.values():
        if isinstance(obj, Data):
            pending = getattr(obj, "_pending_path", None)
            if pending is not None:
                Path(pending).unlink(missing_ok=True)
                delattr(obj, "_pending_path")
    session.info.pop("deleted_data_paths", None)


__all__ = ["Data"]
