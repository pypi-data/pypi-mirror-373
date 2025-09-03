"""Enumeration of lifecycle statuses for entities."""

from __future__ import annotations

from enum import StrEnum


class Status(StrEnum):
    """Lifecycle status for entities."""

    DRAFT = "draft"
    ACTIVE = "active"
    ARCHIVED = "archived"
    DELETED = "deleted"
