"""Custom exceptions used throughout *arbolab*."""

from __future__ import annotations

from dataclasses import dataclass

__all__ = ["MissingOptionalDependency"]


@dataclass
class MissingOptionalDependency(ImportError):
    """Raised when an optional dependency is required but not installed."""

    package: str
    extra: str

    def __post_init__(self) -> None:
        """Compose the error message upon initialisation."""
        message = (
            f"Missing optional dependency '{self.package}'. Install it via "
            f"'pip install arbolab[{self.extra}]' to enable this feature."
        )
        super().__init__(message)
