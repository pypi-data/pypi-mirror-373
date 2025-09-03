import pytest

from arbolab.config import PlotConfig


class DummyLogger:
    def __init__(self) -> None:
        self.messages: list[str] = []

    def warning(self, msg: str, *args: object) -> None:
        self.messages.append(msg % args)


def test_plot_config_invalid_backend_logs_warning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    logger = DummyLogger()
    monkeypatch.setattr("arbolab.log.get_logger", lambda name: logger)
    cfg = PlotConfig(backend="nonexistent")
    cfg.apply()
    assert any("Failed to set matplotlib backend" in message for message in logger.messages)


def test_plot_config_invalid_style_logs_warning(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    logger = DummyLogger()
    monkeypatch.setattr("arbolab.log.get_logger", lambda name: logger)
    cfg = PlotConfig(style="nonexistent-style")
    cfg.apply()
    assert any("Failed to apply matplotlib style" in message for message in logger.messages)
