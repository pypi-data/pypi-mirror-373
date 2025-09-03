import logging
import sys

import pytest

from arbolab.log.color import should_use_colors


def test_should_use_colors_logs_error_when_isatty_fails(
    monkeypatch: pytest.MonkeyPatch, caplog: pytest.LogCaptureFixture
) -> None:
    def raise_oserror() -> bool:  # pragma: no cover - helper
        raise OSError("isatty not supported")

    monkeypatch.setattr(sys.stderr, "isatty", raise_oserror)
    monkeypatch.setattr(sys.stdout, "isatty", raise_oserror)

    with caplog.at_level(logging.ERROR, logger="arbolab.log.color"):
        result = should_use_colors(None)

    assert result is False
    assert any(
        "Failed to determine if output is a TTY" in record.message for record in caplog.records
    )
