import logging
import os
from unittest import mock
from rich.logging import RichHandler
from regscale.core.app.logz import create_logger


def test_create_logger_creates_logger_with_default_settings():
    logger = create_logger()
    assert logger.name == "regscale"
    assert logger.level == logging.INFO


def test_create_logger_respects_propagate_parameter():
    logger = create_logger(propagate=True)
    assert logger.propagate is True


def test_create_logger_adds_custom_handler():
    custom_handler = logging.StreamHandler()
    logger = create_logger(custom_handler=custom_handler)
    assert any(isinstance(handler, logging.StreamHandler) for handler in logger.handlers)


def test_create_logger_with_capture_events_handler():
    from regscale.integrations.public.fedramp.ssp_logger import CaptureEventsHandler

    custom_handler = CaptureEventsHandler([], [], [])
    logger = create_logger(custom_handler=custom_handler)
    assert any(isinstance(handler, CaptureEventsHandler) for handler in logger.handlers)


def test_create_logger_creates_file_handler_when_not_in_container():
    with mock.patch.dict(os.environ, {"REGSCALE_ECS": "False"}):
        logger = create_logger()
        assert any(isinstance(handler, logging.handlers.TimedRotatingFileHandler) for handler in logger.handlers)


def test_create_logger_does_not_create_file_handler_when_in_container():
    with mock.patch.dict(os.environ, {"REGSCALE_ECS": "True"}):
        logger = create_logger()
        assert not any(isinstance(handler, logging.handlers.TimedRotatingFileHandler) for handler in logger.handlers)


def test_create_logger_uses_custom_log_level():
    with mock.patch.dict(os.environ, {"LOGLEVEL": "DEBUG"}):
        logger = create_logger()
        assert logger.level == logging.DEBUG


def test_create_logger_uses_custom_log_width():
    with mock.patch.dict(os.environ, {"REGSCALE_LOG_WIDTH": "100"}):
        logger = create_logger()
        assert any(
            getattr(handler.console, "width", None) == 100
            for handler in logger.handlers
            if isinstance(handler, RichHandler)
        )


def test_create_logger_handles_invalid_log_width():
    with mock.patch.dict(os.environ, {"REGSCALE_LOG_WIDTH": "invalid"}):
        logger = create_logger()
        assert any(
            getattr(handler.console, "width", None) is not None
            for handler in logger.handlers
            if isinstance(handler, RichHandler)
        )


def test_getting_regscale_logger():
    logger = logging.getLogger("regscale")
    assert logger.name == "regscale"
    assert len(logger.handlers) > 0
