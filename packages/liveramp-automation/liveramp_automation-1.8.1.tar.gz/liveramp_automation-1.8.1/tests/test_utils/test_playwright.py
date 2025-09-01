import pytest
import os
import logging
from unittest.mock import Mock, patch
from liveramp_automation.utils.playwright import PlaywrightUtils
from liveramp_automation.utils.time import MACROS
from liveramp_automation.utils.log import Logger


@pytest.fixture
def mock_playwright_page():
    """Provides a mock Playwright page object for testing."""
    mock_page = Mock()
    mock_page.url = 'https://liveramp.com/careers/'
    mock_page.title = 'Liveramp'
    return mock_page


def test_save_screenshot(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    my_page_instance.save_screenshot('test_screenshot')
    assert mock_playwright_page.screenshot.called


def test_save_screenshot_calls_page_screenshot_with_correct_path(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    screenshot_name = "test_screenshot"
    mock_screenshot_dir = "test_dir"
    mocked_now = "20240101_120000"

    with patch.object(my_page_instance, '_get_configured_screenshot_dir_', return_value=mock_screenshot_dir):
        with patch.dict(MACROS, {"now": mocked_now}):
            my_page_instance.save_screenshot(screenshot_name)
            expected_path = os.path.join(mock_screenshot_dir, f"{mocked_now}_{screenshot_name}.png")
            mock_playwright_page.screenshot.assert_called_with(expected_path)


def test_save_screenshot_invalid_filename(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    invalid_screenshot_name = 'test/screenshot:with*invalid?chars'
    my_page_instance.save_screenshot(invalid_screenshot_name)
    assert mock_playwright_page.screenshot.called


def test_save_screenshot_invalid_filename_chars(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    invalid_chars = r":/\\"
    expected_filename = f"{invalid_chars}_test_screenshot.png"
    expected_path = os.path.join('reports', expected_filename)

    with patch.dict('liveramp_automation.utils.time.MACROS', {'now': invalid_chars}):
        with patch.object(PlaywrightUtils, '_get_configured_screenshot_dir_', return_value='reports'):
            my_page_instance.save_screenshot('test_screenshot')
            mock_playwright_page.screenshot.assert_called_with(expected_path)


def test_save_screenshot_exception(mock_playwright_page, caplog):
    mock_playwright_page.screenshot.side_effect = Exception("Screenshot failed")
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    with caplog.at_level(logging.ERROR):
        my_page_instance.save_screenshot('test_screenshot')
    assert "Error saving screenshot: Screenshot failed" in caplog.text


def test_save_screenshot_empty_screenshot_dir(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    with patch.object(my_page_instance, '_get_configured_screenshot_dir_', return_value=''):
        my_page_instance.save_screenshot('test_screenshot')
    assert mock_playwright_page.screenshot.called


def test_navigate_to_url(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    my_page_instance.navigate_to_url(scheme='https', host_name='example.com', path='/test', query='param=value')
    assert mock_playwright_page.goto.called
    mock_playwright_page.goto.assert_called_with('https://example.com/test?param=value')


def test_navigate_to_url_with_partial_arguments(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    my_page_instance.navigate_to_url(path='/about')
    assert mock_playwright_page.goto.called
    mock_playwright_page.goto.assert_called_with('https://liveramp.com/about')


def test_navigate_to_url_no_args(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    my_page_instance.navigate_to_url()
    assert mock_playwright_page.goto.called
    mock_playwright_page.goto.assert_called_with('https://liveramp.com/careers/')


def test_navigate_to_url_exception(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    mock_playwright_page.goto.side_effect = Exception("Navigation failed")
    with patch("liveramp_automation.utils.playwright.Logger.error") as mock_logger_error:
        my_page_instance.navigate_to_url(scheme='https', host_name='example.com', path='/test', query='param=value')
        assert mock_logger_error.called


def test_navigate_to_url_empty_url():
    mock_page = Mock()
    mock_page.url = ''
    my_page_instance = PlaywrightUtils(mock_page)
    my_page_instance.navigate_to_url(scheme='https', host_name='example.com', path='/test', query='param=value')
    assert mock_page.goto.called
    mock_page.goto.assert_called_with('https://example.com/test?param=value')


def test_navigate_to_url_invalid_url(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    mock_playwright_page.goto.side_effect = Exception("Invalid URL")
    my_page_instance.navigate_to_url(scheme=None, host_name=None, path='/test')
    assert mock_playwright_page.goto.called  # Ensure goto is called, even with invalid URL


def test_close_page_banner(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    my_page_instance.close_popup_banner()


def test_close_popup_banner_dialog_button_1_visible(mock_playwright_page):
    """
    Test that close_popup_banner clicks dialog_button_1 and logs the correct message when it is visible.
    """
    my_page_instance = PlaywrightUtils(mock_playwright_page)

    # Mock the locator objects and their is_visible methods
    dialog_button_1 = Mock()
    dialog_button_2 = Mock()
    dialog_button_3 = Mock()

    dialog_button_1.is_visible.return_value = True
    dialog_button_2.is_visible.return_value = False
    dialog_button_3.is_visible.return_value = False

    mock_playwright_page.locator.side_effect = [dialog_button_1, dialog_button_2, dialog_button_3]

    # Mock Logger.debug to capture the log message
    Logger.debug = Mock()

    my_page_instance.close_popup_banner()

    # Assert that dialog_button_1.click() was called
    dialog_button_1.click.assert_called_once()
    Logger.debug.assert_called_with("Banner pendo-button found/close.")


def test_close_popup_banner_dialog_button_2_visible(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)

    # Mock the locator objects and their is_visible methods
    dialog_button_1 = Mock()
    dialog_button_2 = Mock()
    dialog_button_3 = Mock()

    dialog_button_1.is_visible.return_value = False
    dialog_button_2.is_visible.return_value = True
    dialog_button_3.is_visible.return_value = False

    mock_playwright_page.locator.side_effect = [dialog_button_1, dialog_button_2, dialog_button_3]

    # Mock Logger.debug to capture the log message
    Logger.debug = Mock()

    my_page_instance.close_popup_banner()

    # Assert that dialog_button_2.click() was called
    dialog_button_2.click.assert_called_once()
    Logger.debug.assert_called_with("Banner pendo-close found/close.")


def test_close_popup_banner_dialog_button_3_visible(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)

    # Mock the locator objects and their is_visible and click methods
    dialog_button_1 = Mock()
    dialog_button_2 = Mock()
    dialog_button_3 = Mock()

    # Set return values for is_visible()
    dialog_button_1.is_visible.return_value = False
    dialog_button_2.is_visible.return_value = False
    dialog_button_3.is_visible.return_value = True

    # Mock the page.locator calls to return our mock locator objects
    mock_playwright_page.locator.side_effect = [dialog_button_1, dialog_button_2, dialog_button_3]

    # Mock Logger.debug to check the log message
    Logger.debug = Mock()

    # Call the method
    my_page_instance.close_popup_banner()

    # Assert that dialog_button_3.click() was called
    dialog_button_3.click.assert_called_once()

    # Assert that the correct log message was printed
    Logger.debug.assert_called_with("Banner _pendo-close-guide found/close.")


def test_close_popup_banner_no_banners(mock_playwright_page, monkeypatch):
    """
    Test that close_popup_banner logs 'No banners found/close.' when no banners are visible.
    """
    mock_dialog_button_1 = Mock()
    mock_dialog_button_1.is_visible.return_value = False
    mock_dialog_button_2 = Mock()
    mock_dialog_button_2.is_visible.return_value = False
    mock_dialog_button_3 = Mock()
    mock_dialog_button_3.is_visible.return_value = False

    mock_playwright_page.locator.side_effect = [
        mock_dialog_button_1,
        mock_dialog_button_2,
        mock_dialog_button_3,
    ]

    mock_logger = Mock()
    monkeypatch.setattr(Logger, "debug", mock_logger)

    my_page_instance = PlaywrightUtils(mock_playwright_page)
    my_page_instance.close_popup_banner()

    mock_logger.assert_called_with("No banners found/close.")


def test_close_popup_banner_click_raises_exception(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    dialog_button_1_mock = Mock()
    dialog_button_1_mock.is_visible.return_value = True
    dialog_button_1_mock.click.side_effect = Exception("Click failed")

    mock_playwright_page.locator.return_value = dialog_button_1_mock

    try:
        my_page_instance.close_popup_banner()
    except Exception as e:
        assert str(e) == "Click failed"


def test_close_popup_banner_multiple_visible(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)

    # Mock the locator objects and their is_visible and click methods
    dialog_button_1 = Mock()
    dialog_button_2 = Mock()
    dialog_button_3 = Mock()

    dialog_button_1.is_visible.return_value = True
    dialog_button_2.is_visible.return_value = True
    dialog_button_3.is_visible.return_value = False

    mock_playwright_page.locator.side_effect = [dialog_button_1, dialog_button_2, dialog_button_3]

    my_page_instance.close_popup_banner()

    # Assert that only the first button's click method was called
    dialog_button_1.click.assert_called_once()
    dialog_button_2.click.assert_not_called()
    dialog_button_3.click.assert_not_called()


def test_close_popup_banner_becomes_visible(mock_playwright_page):
    my_page_instance = PlaywrightUtils(mock_playwright_page)
    mock_locator = Mock()
    mock_locator.is_visible.side_effect = [False, True]
    mock_playwright_page.locator.return_value = mock_locator
    my_page_instance.close_popup_banner()
    assert mock_locator.click.called


@patch('liveramp_automation.utils.playwright.FileHelper.read_init_file')
def test_get_configured_screenshot_dir_with_pytest_ini_and_key(mock_read_init_file, mock_playwright_page):
    """
    Tests that _get_configured_screenshot_dir_ returns the directory from pytest.ini
    when the file exists and contains the 'screenshot' key.
    """
    # Arrange
    expected_dir = 'custom/screenshots'
    mock_read_init_file.return_value = {'screenshot': expected_dir}
    playwright_utils = PlaywrightUtils(mock_playwright_page)

    # Act
    actual_dir = playwright_utils._get_configured_screenshot_dir_()

    # Assert
    assert actual_dir == expected_dir
    mock_read_init_file.assert_called_once()


@patch('liveramp_automation.utils.playwright.FileHelper.read_init_file')
def test_get_configured_screenshot_dir_with_pytest_ini_without_key(mock_read_init_file, mock_playwright_page):
    """
    Tests that _get_configured_screenshot_dir_ returns the default directory
    when pytest.ini exists but does not contain the 'screenshot' key.
    """
    # Arrange
    mock_read_init_file.return_value = {'some_other_key': 'some_other_value'}
    playwright_utils = PlaywrightUtils(mock_playwright_page)
    expected_dir = 'reports'  # Default screenshot directory

    # Act
    actual_dir = playwright_utils._get_configured_screenshot_dir_()

    # Assert
    assert actual_dir == expected_dir
    mock_read_init_file.assert_called_once()


@patch('liveramp_automation.utils.playwright.FileHelper.read_init_file')
def test_get_configured_screenshot_dir_no_pytest_ini(mock_read_init_file, mock_playwright_page):
    """
    Tests that _get_configured_screenshot_dir_ returns the default directory
    when pytest.ini does not exist.
    """
    # Arrange
    mock_read_init_file.return_value = {}
    playwright_utils = PlaywrightUtils(mock_playwright_page)
    expected_dir = playwright_utils.default_screenshot_dir

    # Act
    actual_dir = playwright_utils._get_configured_screenshot_dir_()

    # Assert
    assert actual_dir == expected_dir
    mock_read_init_file.assert_called_once()


@patch('liveramp_automation.utils.playwright.FileHelper.read_init_file')
def test_get_configured_screenshot_dir_exception(mock_read_init_file, mock_playwright_page):
    """
    Tests that _get_configured_screenshot_dir_ returns the default directory
    when an exception occurs while reading the pytest.ini file.
    """
    # Arrange
    mock_read_init_file.side_effect = Exception("Failed to read ini file")
    playwright_utils = PlaywrightUtils(mock_playwright_page)
    expected_dir = 'reports'

    # Act
    actual_dir = playwright_utils._get_configured_screenshot_dir_()

    # Assert
    assert actual_dir == expected_dir
    mock_read_init_file.assert_called_once()


@patch('liveramp_automation.utils.playwright.FileHelper.read_init_file')
def test_get_configured_screenshot_dir_file_not_found(mock_read_init_file, mock_playwright_page):
    """
    Tests that _get_configured_screenshot_dir_ returns the default directory
    when pytest.ini is not found.
    """
    # Arrange
    mock_read_init_file.side_effect = FileNotFoundError
    playwright_utils = PlaywrightUtils(mock_playwright_page)
    expected_dir = playwright_utils.default_screenshot_dir

    # Act
    actual_dir = playwright_utils._get_configured_screenshot_dir_()

    # Assert
    assert actual_dir == expected_dir
    mock_read_init_file.assert_called_once()