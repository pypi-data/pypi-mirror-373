from unittest.mock import MagicMock, patch

from arbolab.utils.runtime import log_runtime


def test_log_runtime_context_manager_logging() -> None:
    logger = MagicMock()
    with patch("arbolab.utils.runtime.get_logger", return_value=logger):
        with log_runtime("work"):
            pass
        logger.log.assert_called_once()

        logger.log.reset_mock()
        with log_runtime("work", enabled=False):
            pass
        logger.log.assert_not_called()


def test_log_runtime_decorator_logging() -> None:
    logger = MagicMock()
    with patch("arbolab.utils.runtime.get_logger", return_value=logger):

        @log_runtime("func")
        def decorated() -> None:
            pass

        decorated()
        logger.log.assert_called_once()

        logger.log.reset_mock()

        @log_runtime("func", enabled=False)
        def decorated_disabled() -> None:
            pass

        decorated_disabled()
        logger.log.assert_not_called()
