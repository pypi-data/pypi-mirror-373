import logging
from io import StringIO

import pytest

from ms_utils.logging_lib import Logger


@pytest.fixture
def logger_name():
    return "test_logger"


@pytest.fixture
def log_file():
    return "./tests/data/test.log"


@pytest.fixture
def log_message():
    return "This is a test log message"


def test_setup_logger_with_stream_handler(logger_name):
    logger = Logger.setup_logger(logger_name, log_file=None)
    assert logger.name == logger_name
    assert logger.level == logging.INFO
    assert any(
        isinstance(handler, logging.StreamHandler)
        for handler in logger.handlers
    )


def test_setup_logger_with_file_handler(log_file):
    logger = Logger.setup_logger("test_logger_file", log_file=str(log_file))
    assert any(
        isinstance(handler, logging.FileHandler) for handler in logger.handlers
    )


def test_add_file_handler(logger_name, log_file):
    logger = logging.getLogger(logger_name)
    Logger.add_file_handler(logger, str(log_file))
    assert any(
        isinstance(handler, logging.FileHandler) for handler in logger.handlers
    )


def test_add_stream_handler(logger_name):
    logger = logging.getLogger(logger_name)
    Logger.add_stream_handler(logger)
    assert any(
        isinstance(handler, logging.StreamHandler)
        for handler in logger.handlers
    )


def test_set_level(logger_name):
    logger = logging.getLogger(logger_name)
    Logger.set_level(logger, logging.DEBUG)
    assert logger.level == logging.DEBUG


def test_create_formatter_default():
    formatter = Logger.create_formatter()
    assert isinstance(formatter, logging.Formatter)
    assert (
        formatter._fmt
        == "[%(levelname)s] [%(asctime)s] (%(module)s:%(lineno)d) -> %(message)s"
    )


def test_create_formatter_custom():
    fmt = "%(name)s - %(levelname)s - %(message)s"
    datefmt = "%Y-%m-%d %H:%M:%S"
    formatter = Logger.create_formatter(fmt=fmt, datefmt=datefmt)
    assert isinstance(formatter, logging.Formatter)
    assert formatter._fmt == fmt
    assert formatter.datefmt == datefmt


def test_logging_to_stream(logger_name, log_message):
    logger = Logger.setup_logger(logger_name)
    log_output = StringIO()
    stream_handler = logging.StreamHandler(log_output)
    logger.addHandler(stream_handler)

    logger.info(log_message)
    log_output.seek(0)
    output = log_output.read()

    assert log_message in output


def test_logging_to_file(logger_name, log_file, log_message):
    logger = Logger.setup_logger(logger_name, log_file=str(log_file))

    logger.info(log_message)

    with open(log_file, "r") as f:
        log_contents = f.read()

    assert log_message in log_contents
