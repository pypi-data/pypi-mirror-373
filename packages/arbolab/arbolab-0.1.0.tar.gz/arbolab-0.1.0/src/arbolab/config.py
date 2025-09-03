"""Application configuration utilities built on Pydantic models."""

from __future__ import annotations

from collections.abc import Generator, Mapping
from contextlib import contextmanager
from pathlib import Path
from typing import Any

import yaml
from pydantic import AliasChoices, BaseModel, Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from .exceptions import MissingOptionalDependency
from .utils import path as pathutil
from .utils.path import PathLike


class LoggingConfig(BaseModel):
    """Configuration for the logging subsystem."""

    level: str | None = Field(default="INFO", validation_alias=AliasChoices("level", "log_level"))
    use_colors: bool | None = None
    save_to_file: bool = False
    tune_matplotlib: bool = False

    @field_validator("level")
    @classmethod
    def _normalise_level(cls, value: str | None) -> str | None:
        """Ensure log level values are upper case."""
        if value is None:
            return None
        return str(value).upper()


class DBConfig(BaseModel):
    """Database related configuration."""

    echo: bool = False
    engine_kwargs: dict[str, object] = Field(default_factory=dict)


@contextmanager
def _require_matplotlib(module: str) -> Generator[object, None, None]:
    """Import a Matplotlib module or raise a consistent dependency error."""
    try:
        yield __import__(module, fromlist=["*"])
    except ImportError as exc:  # pragma: no cover - dependency missing
        raise MissingOptionalDependency("matplotlib", "plot") from exc


class PlotConfig(BaseModel):
    """Plotting related configuration."""

    backend: str | None = None
    style: str | None = None

    def apply(self) -> None:
        """Apply configured Matplotlib backend and style."""
        from .log import get_logger

        logger = get_logger(__name__)
        if self.backend:
            with _require_matplotlib("matplotlib") as matplotlib:
                try:
                    matplotlib.use(self.backend)
                except (
                    ImportError,
                    ValueError,
                    RuntimeError,
                ) as exc:  # pragma: no cover - backend errors not easily simulated
                    logger.warning(
                        "Failed to set matplotlib backend '%s': %s",
                        self.backend,
                        exc,
                    )
        if self.style:
            with _require_matplotlib("matplotlib.pyplot") as plt:
                try:
                    plt.style.use(self.style)
                except (
                    OSError,
                    ValueError,
                ) as exc:  # pragma: no cover - style errors not easily simulated
                    logger.warning(
                        "Failed to apply matplotlib style '%s': %s",
                        self.style,
                        exc,
                    )


class Config(BaseSettings):
    """Basic configuration for the Lab."""

    working_dir: Path | None = None
    db_url: str | None = None
    db: DBConfig = Field(default_factory=DBConfig)
    plot: PlotConfig = Field(default_factory=PlotConfig)
    logging: LoggingConfig = Field(default_factory=LoggingConfig)

    model_config = SettingsConfigDict(
        env_prefix="ARBOLAB_",
        env_nested_delimiter="__",
        validate_assignment=True,
    )

    @field_validator("working_dir", mode="before")
    @classmethod
    def _validate_working_dir(cls, value: PathLike | None) -> Path | None:
        """Normalise and create the working directory if provided."""
        if value is None:
            return None
        path = Path(value)
        path.mkdir(parents=True, exist_ok=True)
        return path

    # ------------------------------------------------------------------
    @property
    def log_level(self) -> str | None:
        """Top-level access to the logging level."""
        return self.logging.level

    @log_level.setter
    def log_level(self, value: str | None) -> None:
        if value is not None:
            self.logging.level = str(value).upper()

    # ------------------------------------------------------------------
    def to_dict(self) -> dict[str, Any]:
        """Return a JSON-serialisable representation of the config."""
        data = self.model_dump(exclude_none=True)
        if data.get("working_dir") is not None:
            data["working_dir"] = str(data["working_dir"])
        return data

    # ------------------------------------------------------------------
    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Config:
        """Create a Config instance from a dictionary."""
        return cls.model_validate(data)

    # ------------------------------------------------------------------
    @classmethod
    def from_env(cls) -> Config:
        """Create a configuration from environment variables."""
        return cls()

    # ------------------------------------------------------------------
    @classmethod
    def from_file(cls, path: PathLike) -> Config:
        """Load configuration from a YAML file."""
        path = pathutil.to_path(path)
        if path is None:  # pragma: no cover - input type enforced
            raise TypeError("path must be a valid file path")
        try:
            with open(path, encoding="utf-8") as fh:
                data = yaml.safe_load(fh) or {}
        except FileNotFoundError as exc:  # pragma: no cover - file missing
            raise FileNotFoundError("Config file not found") from exc
        except yaml.YAMLError as exc:  # pragma: no cover - invalid YAML
            raise ValueError("Invalid YAML") from exc
        return cls.from_dict(data)


__all__ = ["Config", "DBConfig", "LoggingConfig", "PlotConfig"]
