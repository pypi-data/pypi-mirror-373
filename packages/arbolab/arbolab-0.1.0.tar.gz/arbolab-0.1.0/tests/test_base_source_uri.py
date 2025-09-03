"""Tests for :class:`BaseEntity`'s ``source_uri`` property."""

from __future__ import annotations

from arbolab.classes.base import BaseEntity, table_name


class DummyEntity(BaseEntity):
    """Minimal concrete entity for testing purposes."""

    __tablename__ = table_name("dummy_entity")


def test_source_uri_returns_only_str_or_none() -> None:
    entity = DummyEntity(provenance={})

    # Regular case: stored value is a string
    entity.provenance["source_uri"] = "https://example.org"
    assert entity.source_uri == "https://example.org"

    # Any non-string value should be ignored and None returned
    entity.provenance["source_uri"] = 123  # type: ignore[assignment]
    assert entity.source_uri is None
