import os
from urllib.parse import urlparse, urlunsplit

from liveramp_automation.helpers.file import FileHelper
from liveramp_automation.utils.allure import allure_attach_text
from liveramp_automation.utils.log import Logger
from liveramp_automation.utils.time import MACROS


class PlaywrightUtils:
    """
    Utility class for Playwright operations.

    This class provides methods for navigating URLs and capturing screenshots using Playwright.

    :param page: Playwright page object.
    :type page: Playwright Page
    """

    def __init__(self, page):
        """
        Initialize PlaywrightUtils with a page object.

        :param page: Playwright page object.
        """
        self.page = page
        self.default_screenshot_dir = 'reports'

    def navigate_to_url(self, scheme=None, host_name=None, path=None, query=None):
        """
        Navigate to a URL with optional components.

        :param scheme: URL scheme (e.g., 'http', 'https').
        :param host_name: Host name or IP address.
        :param path: URL path.
        :param query: URL query string.
        :return: None
        """
        parsed_uri = urlparse(self.page.url)
        url = urlunsplit((parsed_uri.scheme if scheme is None else scheme,
                          parsed_uri.hostname if host_name is None else host_name,
                          parsed_uri.path if path is None else path,
                          parsed_uri.query if query is None else query,
                          ''))
        Logger.debug("Navigating to: {}".format(url))
        allure_attach_text("Navigating to:", url)
        try:
            self.page.goto(url)
        except Exception as error:
            Logger.error("An error occurred while navigating: {}".format(error))

    def _get_configured_screenshot_dir_(self):
        """Get the configured screenshot directory from the pytest.ini file or use the default.
        If pytest.ini file has not set up the default directory for screenshot,
        it will use the reports directory instead.
        """
        try:
            config_data = FileHelper.read_init_file(os.getcwd(), "pytest.ini", "r")
            Logger.debug("Pytest ini file context: {}".format(config_data))
            screenshot_dir = config_data.get('screenshot', self.default_screenshot_dir)
            return screenshot_dir
        except Exception as e:
            Logger.error(f"Error reading screenshot configuration: {str(e)}")
            return self.default_screenshot_dir

    def save_screenshot(self, screenshot_name):
        """
        Save a screenshot of the current page.

        :param screenshot_name: Name for the saved screenshot.
        :return: None
        """
        try:
            screenshot_dir = self._get_configured_screenshot_dir_()
            screenshot_filename = "{}_{}.png".format(MACROS["now"], screenshot_name)
            screenshot_path = os.path.join(screenshot_dir, screenshot_filename)
            self.page.screenshot(screenshot_path)
            Logger.debug(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            Logger.error(f"Error saving screenshot: {str(e)}")

    def close_popup_banner(self):
        """
        Close the popup banner using a matched CSS selector pattern.

        :return: None
        """
        dialog_button_1 = self.page.locator('button[id^="pendo-button"]')
        dialog_button_2 = self.page.locator('button[id^="pendo-close"]')
        dialog_button_3 = self.page.locator('button[id="_pendo-close-guide"]')

        if dialog_button_1.is_visible():
            dialog_button_1.click()
            Logger.debug("Banner pendo-button found/close.")
        elif dialog_button_2.is_visible():
            dialog_button_2.click()
            Logger.debug("Banner pendo-close found/close.")
        elif dialog_button_3.is_visible():
            dialog_button_3.click()
            Logger.debug("Banner _pendo-close-guide found/close.")
        else:
            Logger.debug("No banners found/close.")
