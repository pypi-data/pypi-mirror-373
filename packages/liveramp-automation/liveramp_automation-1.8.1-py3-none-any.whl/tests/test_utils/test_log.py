import logging
import pytest
from unittest.mock import patch, mock_open
from liveramp_automation.utils.log import LoggerUtils, MyFormatter, Logger
import os


def test_log_info():
    Logger.info("info")


def test_log_critical():
    Logger.critical("critical")


def test_log_error():
    Logger.error("Error")


def test_log_debug():
    Logger.debug("Debug")


def test_log_warning():
    Logger.warning("warning")


def test_get_logger_returns_same_instance():
    logger_utils = LoggerUtils()
    logger1 = logger_utils.get_logger()
    logger2 = logger_utils.get_logger()
    assert logger1 == logger2


def test_get_logger_returns_same_instance_from_different_utils():
    logger_utils1 = LoggerUtils()
    logger_utils2 = LoggerUtils()
    logger1 = logger_utils1.get_logger()
    logger2 = logger_utils2.get_logger()
    assert logger1 is logger2


def test_get_logger_returns_logger_instance():
    logger = LoggerUtils.get_logger()
    assert isinstance(logger, logging.Logger)


def test_get_logger_raises_exception_on_first_call(monkeypatch):
    """
    Tests that if _configure_logging raises an exception, subsequent calls to get_logger
    will also raise the same exception.
    """
    
    def mock_configure_logging():
        raise Exception("Failed to configure logging")

    LoggerUtils._instance = None  # Reset _instance to None before the test
    monkeypatch.setattr(LoggerUtils, "_configure_logging", mock_configure_logging)

    with pytest.raises(Exception, match="Failed to configure logging"):
        LoggerUtils.get_logger()

    # Subsequent call should also raise the exception
    with pytest.raises(Exception, match="Failed to configure logging"):
        LoggerUtils.get_logger()


def test_configure_logging_returns_logger_instance():
    logger_utils = LoggerUtils()
    logger = logger_utils._configure_logging()
    assert isinstance(logger, logging.Logger)


def test_get_log_format_returns_my_formatter_when_scenario_included(monkeypatch):
    logger_utils = LoggerUtils()
    monkeypatch.setenv("SCENARIO_NAME", "test_scenario")
    log_format = logger_utils.get_log_format("true")
    assert isinstance(log_format, MyFormatter)
    assert "test_case_name" in log_format._fmt


def test_get_log_format_returns_my_formatter_when_scenario_included_yes(monkeypatch):
    logger_utils = LoggerUtils()
    monkeypatch.setenv("SCENARIO_NAME", "test_scenario")
    log_format = logger_utils.get_log_format("yes")
    assert isinstance(log_format, MyFormatter)
    assert "test_case_name" in log_format._fmt


def test_get_log_format_returns_my_formatter_when_scenario_included_mixed_case(monkeypatch):
    logger_utils = LoggerUtils()
    monkeypatch.setenv("SCENARIO_NAME", "test_scenario")
    log_format = logger_utils.get_log_format("TrUe")
    assert isinstance(log_format, MyFormatter)
    assert "test_case_name" in log_format._fmt


def test_get_log_format_returns_my_formatter_when_scenario_included_numeric_string(monkeypatch):
    logger_utils = LoggerUtils()
    monkeypatch.setenv("SCENARIO_NAME", "test_scenario")
    log_format = logger_utils.get_log_format("1")
    assert isinstance(log_format, MyFormatter)
    assert "test_case_name" in log_format._fmt


def test_get_log_format_returns_default_formatter_when_scenario_not_included(monkeypatch):
    logger_utils = LoggerUtils()
    monkeypatch.delenv("SCENARIO_NAME", raising=False)
    log_format = logger_utils.get_log_format("false")
    assert isinstance(log_format, logging.Formatter)
    assert "test_case_name" not in log_format._fmt


def test_get_log_format_returns_default_formatter_when_scenario_not_included_numeric_string(monkeypatch):
    logger_utils = LoggerUtils()
    monkeypatch.delenv("SCENARIO_NAME", raising=False)
    log_format = logger_utils.get_log_format("0")
    assert isinstance(log_format, logging.Formatter)
    assert "test_case_name" not in log_format._fmt


def test_logger_utils_get_log_format_invalid_value():
    with pytest.raises(ValueError):
        LoggerUtils.get_log_format('invalid')


def test_logger_utils_get_log_format_empty_string():
    with pytest.raises(ValueError):
        LoggerUtils.get_log_format('')


def test_configure_logging_file_property_not_found():
    with patch('builtins.open', mock_open(read_data="[data]")):
        logger_utils = LoggerUtils()
        logger = logger_utils._configure_logging()
        assert isinstance(logger, logging.Logger)


def test_configure_logging_no_pytest_ini():
    with patch('builtins.open', side_effect=FileNotFoundError), \
         patch('logging.getLogger', return_value=logging.Logger('fresh_logger')):
        logger_utils = LoggerUtils()
        logger = logger_utils._configure_logging()
        assert len(logger.handlers) == 1
        assert isinstance(logger.handlers[0], logging.StreamHandler)
        assert isinstance(logger.handlers[0].formatter, logging.Formatter)
        assert logger.handlers[0].level == logging.INFO


def test_configure_logging_invalid_log_level():
    config_data = """
    [log]
    log_path = reports/
    log_name = %%Y%%m%%d%%H%%M%%S.log
    log_file_level = INVALID_LEVEL
    log_console_level = DEBUG
    log_include_scenario = false
    """
    with patch('builtins.open', mock_open(read_data=config_data)):
        logger_utils = LoggerUtils()
        with pytest.raises(ValueError, match="Unknown level: 'INVALID_LEVEL'"):
            logger_utils._configure_logging()


def test_my_formatter_format_injects_scenario_name_from_env(monkeypatch):
    """
    Tests that MyFormatter.format correctly injects the SCENARIO_NAME
    environment variable into the log record and the final formatted string
    when the environment variable is set.
    """
    # Arrange: Set the environment variable and create necessary objects
    test_scenario_name = "happy_path_scenario_123"
    monkeypatch.setenv("SCENARIO_NAME", test_scenario_name)

    formatter = MyFormatter()
    log_record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_file.py",
        lineno=10,
        msg="A test log message.",
        args=(),
        exc_info=None,
    )

    # Act: Call the format method
    formatted_string = formatter.format(log_record)

    # Assert: Verify the record was modified and the output is correct
    # 1. Verify the 'test_case_name' attribute was added to the record object
    assert hasattr(log_record, 'test_case_name')
    assert log_record.test_case_name == test_scenario_name

    # 2. Verify the formatted string contains the scenario name as per the format
    expected_substring = f"[ {test_scenario_name} ]"
    assert expected_substring in formatted_string

    # 3. Verify the original message is still present in the final output
    assert log_record.msg in formatted_string


def test_my_formatter_format_raises_key_error_when_scenario_name_not_set(monkeypatch):
    """
    Tests that MyFormatter.format raises a KeyError when the SCENARIO_NAME
    environment variable is not set.
    """
    # Arrange: Ensure the environment variable is not set
    monkeypatch.delenv("SCENARIO_NAME", raising=False)

    formatter = MyFormatter()
    log_record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_file.py",
        lineno=10,
        msg="A test log message.",
        args=(),
        exc_info=None,
    )

    # Act & Assert: Verify that a KeyError is raised
    with pytest.raises(KeyError):
        formatter.format(log_record)


def test_my_formatter_format_overwrites_existing_test_case_name(monkeypatch):
    """
    Tests that MyFormatter.format overwrites the test_case_name attribute
    if it already exists in the log record.
    """
    # Arrange: Set the environment variable and create necessary objects
    test_scenario_name = "new_scenario_name"
    monkeypatch.setenv("SCENARIO_NAME", test_scenario_name)

    formatter = MyFormatter()
    log_record = logging.LogRecord(
        name="test_logger",
        level=logging.INFO,
        pathname="test_file.py",
        lineno=10,
        msg="A test log message.",
        args=(),
        exc_info=None,
    )
    log_record.test_case_name = "original_scenario_name"  # Set the attribute initially

    # Act: Call the format method
    formatted_string = formatter.format(log_record)

    # Assert: Verify the record was modified and the output is correct
    # 1. Verify the 'test_case_name' attribute was added to the record object
    assert hasattr(log_record, 'test_case_name')
    assert log_record.test_case_name == test_scenario_name  # Verify it's overwritten

    # 2. Verify the formatted string contains the scenario name as per the format
    expected_substring = f"[ {test_scenario_name} ]"
    assert expected_substring in formatted_string

    # 3. Verify the original message is still present in the final output
    assert log_record.msg in formatted_string


def test_get_log_format_returns_default_formatter_when_scenario_not_included_mixed_case():
    logger_utils = LoggerUtils()
    log_format = logger_utils.get_log_format("FaLsE")
    assert isinstance(log_format, logging.Formatter)
    assert "test_case_name" not in log_format._fmt


@pytest.mark.parametrize("log_include_scenario_value", ["no", "0", "false"])
def test_get_log_format_returns_default_formatter_when_scenario_not_included_variants(log_include_scenario_value):
    logger_utils = LoggerUtils()
    log_format = logger_utils.get_log_format(log_include_scenario_value)
    assert isinstance(log_format, logging.Formatter)
    assert "test_case_name" not in log_format._fmt


def test_get_log_format_sets_scenario_name_to_empty_string_if_not_exists(monkeypatch):
    logger_utils = LoggerUtils()
    monkeypatch.delenv("SCENARIO_NAME", raising=False)
    logger_utils.get_log_format("true")
    assert os.environ["SCENARIO_NAME"] == ""


def test_get_log_format_handles_missing_scenario_name_gracefully(monkeypatch):
    """
    Test that the format method handles missing SCENARIO_NAME gracefully by setting it to empty string.
    """
    logger_utils = LoggerUtils()
    monkeypatch.delenv("SCENARIO_NAME", raising=False)
    log_format = logger_utils.get_log_format("true")
    record = logging.LogRecord(
        name='test', level=logging.INFO, pathname='test.py', lineno=10,
        msg='Test message', args=(), exc_info=None, func='test_func', sinfo=None
    )
    formatted_message = log_format.format(record)
    assert isinstance(formatted_message, str)


def test_get_log_format_scenario_name_deleted(monkeypatch, caplog):
    logger_utils = LoggerUtils()
    monkeypatch.setenv("SCENARIO_NAME", "test_scenario")
    log_format = logger_utils.get_log_format("true")
    assert isinstance(log_format, MyFormatter)
    monkeypatch.delenv("SCENARIO_NAME")

    with caplog.at_level(logging.ERROR):
        with pytest.raises(KeyError):
            record = logging.LogRecord(
                name='test', level=logging.INFO, pathname='test.py', lineno=1,
                msg='test message', args=(), exc_info=None
            )
            log_format.format(record)


def test_logger_during_shutdown():
    # Simulate a shutdown-like state by potentially unsetting the logger instance.
    # Note: We don't actually unset it to avoid interfering with other tests,
    # but this represents the state where some modules might be unavailable.

    # Attempt to use the logger. This should not raise an exception.
    try:
        Logger.info("Testing logger during shutdown")
        assert True  # If we reach here without an exception, the test passes.
    except Exception as e:
        assert False, f"Logger raised an unexpected exception: {e}"


def test_get_log_format_uses_empty_string_for_scenario_name_when_not_set(monkeypatch):
    logger_utils = LoggerUtils()
    monkeypatch.delenv("SCENARIO_NAME", raising=False)
    log_format = logger_utils.get_log_format("true")
    assert isinstance(log_format, MyFormatter)
    assert "test_case_name" in log_format._fmt
    # Verify that the SCENARIO_NAME is set to empty string
    assert os.environ["SCENARIO_NAME"] == ""