import os
from urllib.parse import urlparse, urlunsplit
from liveramp_automation.helpers.file import FileHelper
from liveramp_automation.utils.log import Logger
from liveramp_automation.utils.time import MACROS, fixed_wait
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, JavascriptException, NoSuchElementException, WebDriverException
from selenium.common.exceptions import NoSuchWindowException


class SeleniumUtils:
    DEFAULT_WAIT_TIME = 4
    SHORT_WAIT_TIME = 2
    LONG_WAIT_TIME = 10

    def __init__(self, driver):
        self.driver = driver
        self.default_screenshot_dir = 'reports'

    def navigate_to_url(self, scheme=None, host_name=None, path=None, query=None):
        """Navigate to the provided URL.

        :param scheme: The protocol to use for the connection, such as 'https' or 'http'.
        :param host_name: The domain name of the web server, e.g., 'www.google.com'.
        :param path: The specific route or location on the web server, e.g., '/query/vi/save'.
        :param query: Additional parameters to customize the request.
        :return: None
        """
        try:
            current_url = self.driver.current_url
            Logger.debug(f"Current URL: {str(current_url)}")
            parsed_uri = urlparse(current_url)
            if scheme is None:
                scheme = parsed_uri.scheme
                Logger.debug(f"Current scheme: {str(scheme)}")
            if host_name is None:
                host_name = parsed_uri.netloc
                Logger.debug(f"Current host_name: {str(host_name)}")
            if path is None:
                path = parsed_uri.path
            if query is None:
                query = parsed_uri.query
            new_url = urlunsplit((scheme, host_name, path, query, ''))
            self.driver.get(new_url)
            Logger.debug(f"Navigating to URL: {str(new_url)}")
        except Exception as e:
            Logger.error(f"Error navigating to URL: {str(e)}")

    def _get_configured_screenshot_dir(self):
        """If there is no configured folder, use the default one(preferred).
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

    def save_screenshot(self, screenshot_name: str):
        """ Save a screenshot to the specified destination.
        :param screenshot_name: The desired name for the screenshot file.
        :return: None
        """
        try:
            screenshot_dir = self._get_configured_screenshot_dir()
            screenshot_filename = "{}_{}.png".format(MACROS["now"], screenshot_name)
            screenshot_path = os.path.join(screenshot_dir, screenshot_filename)
            self.driver.save_screenshot(screenshot_path)
            Logger.debug(f"Screenshot saved: {screenshot_path}")
        except Exception as e:
            Logger.error(f"Error saving screenshot: {str(e)}")

    def get_url(self, url):
        """ Open the page using the provided URL.

        :param url:The URL of the page to be opened.
        :return:None
        """
        try:
            parsed_url = urlparse(url)
            if not parsed_url.scheme or not parsed_url.netloc:
                raise ValueError("Invalid URL format. Please provide a valid URL.")
            self.driver.get(url)
            Logger.debug(f"Opened URL: {url}")
        except Exception as e:
            Logger.error(f"Error opening URL: {str(e)}")

    def get_page_url(self):
        """ Get the current page's URL.

        :return: The current page's URL as a string or None if an error occurs.
        """
        try:
            current_url = self.driver.current_url
            Logger.debug(f"Current URL: {current_url}")
            return current_url
        except Exception as e:
            Logger.error(f"Error getting page URL: {str(e)}")
            return None

    def refresh_page(self):
        """ Refresh the page.

        :return: True if the page was successfully refreshed, False otherwise.
        """
        try:
            self.driver.refresh()
            Logger.debug(f"Page Refreshed: {self.driver.current_url}")
            return True
        except Exception as e:
            Logger.error(f"Error refreshing page: {str(e)}")
            return False

    def find_element_by_dict(self, dictionary, seconds: int = LONG_WAIT_TIME):
        """ Retrieve the first element that matches the criteria specified in the dictionary.

        :param dictionary: A dictionary containing criteria for element identification.
        :param seconds: The maximum time, in seconds, to wait for the element to appear (default is 5 seconds).
        :return: The found element or None if not found.
        """
        by_type = (next(iter(dictionary)))
        locator = dictionary.get(by_type)
        try:
            return WebDriverWait(self.driver, seconds).until(EC.presence_of_element_located((by_type, locator)))
        except TimeoutException:
            Logger.debug("Element {} was not found".format(locator))
            return None

    def find_elements_by_dict(self, dictionary, seconds: int = LONG_WAIT_TIME):
        """ Search for all elements that match the criteria specified in the dictionary.

        :param dictionary: A dictionary containing criteria for element identification.
        :param seconds: The maximum time, in seconds, to wait for elements to appear.
        :return: A list of found elements, which can be empty if no elements are found.
        """
        by_type = (next(iter(dictionary)))
        locator = dictionary.get(by_type)
        try:
            return WebDriverWait(self.driver, seconds).until(
                EC.presence_of_all_elements_located((by_type, locator)))
        except TimeoutException:
            Logger.debug("Element {} was not found".format(locator))

    def find_element(self, by_type, locator, seconds: int = LONG_WAIT_TIME):
        """ Locate the first element and wait for it to load within the specified maximum seconds time.

        :param by_type: The method used for locating the element, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator, such as an ID, name, or XPath expression.
        :param seconds: The maximum time, in seconds, to wait for the element to appear.
        :return: The found element or None if not found.
        """
        try:
            return WebDriverWait(self.driver, seconds).until(EC.presence_of_element_located((by_type, locator)))
        except TimeoutException:
            Logger.debug("Element {} was not found".format(locator))
            return None

    def find_element_by_css(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for the first element using the CSS_SELECTOR with the implementation of Explicit Waits.

        :param locator: The CSS selector used to locate the element.
        :param seconds: The maximum time, in seconds, to wait for the element to appear.
        :return: The found element or None if not found.
        """
        return self.find_element(By.CSS_SELECTOR, locator, seconds)

    def find_element_by_xpath(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for the first element using the XPATH with the implementation of Explicit Waits.

        :param locator: The XPATH used to locate the element.
        :param seconds: The maximum time, in seconds, to wait for the element to appear.
        :return: The found element or None if not found.
        """
        return self.find_element(By.XPATH, locator, seconds)

    def find_element_by_name(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for the first element using the Name with the implementation of Explicit Waits.

        :param locator: The NAME used to locate the element.
        :param seconds: The maximum time, in seconds, to wait for the element to appear.
        :return: The found element or None if not found.
        """
        return self.find_element(By.NAME, locator, seconds)

    def find_element_by_tag(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for the first element using the TAG_NAME with the implementation of Explicit Waits.

        :param locator: The CSS selector used to locate the element.
        :param seconds: The maximum time, in seconds, to wait for the element to appear.
        :return: The found element or None if not found.
        """
        return self.find_element(By.TAG_NAME, locator, seconds)

    def find_element_by_id(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for the first element using the ID with the implementation of Explicit Waits.

        :param locator: The ID used to locate the element.
        :param seconds: The maximum time, in seconds, to wait for the element to appear.
        :return: The found element or None if not found.
        """
        return self.find_element(By.ID, locator, seconds)

    def find_element_by_link_text(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for the first element using the LINK_TEXT with the implementation of Explicit Waits.

        :param locator: The LINK_TEXT used to locate the element.
        :param seconds: The maximum time, in seconds, to wait for the element to appear.
        :return: The found element or None if not found.
        """
        return self.find_element(By.LINK_TEXT, locator, seconds)

    def find_element_by_partial_link_text(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for the first element using the PARTIAL_LINK_TEXT with the implementation of Explicit Waits.

        :param locator: The PARTIAL_LINK_TEXT used to locate the element.
        :param seconds: The maximum time, in seconds, to wait for the element to appear.
        :return: The found element or None if not found.
        """
        return self.find_element(By.PARTIAL_LINK_TEXT, locator, seconds)

    def find_element_by_class_name(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for multiple elements using the CLASS_NAME method and implement Explicit Waits.

        :param locator: The CLASS_NAME used to locate the elements.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear.
        :return: A list of found elements, which can be empty if no elements are found.
        """
        return self.find_element(By.CLASS_NAME, locator, seconds)

    def find_elements(self, by_type, locator, seconds: int = LONG_WAIT_TIME):
        """ Find multiple elements using the specified method and locator, and wait for them
        to load within the specified maximum seconds: int = LONG_WAIT_TIME time.

        :param by_type: The method used for locating the elements, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator, such as an ID, name, or XPath expression.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear.
        :return: A list of found elements, which can be empty if no elements are found.
        """
        try:
            return WebDriverWait(self.driver, seconds).until(
                EC.presence_of_all_elements_located((by_type, locator)))
        except TimeoutException:
            Logger.debug("Element {} was not found".format(locator))

    def find_elements_by_css(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for multiple elements using the CSS_SELECTOR method and implement Explicit Waits.

        :param locator: The CSS selector used to locate the elements.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear.
        :return: A list of found elements, which can be empty if no elements are found.
        """
        return self.find_elements(By.CSS_SELECTOR, locator, seconds)

    def find_elements_by_class_name(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for multiple elements using the CLASS_NAME method and implement Explicit Waits.

        :param locator: The CLASS_NAME used to locate the elements.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear.
        :return: A list of found elements, which can be empty if no elements are found.
        """
        return self.find_elements(By.CLASS_NAME, locator, seconds)

    def find_elements_by_id(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for multiple elements using the ID method and implement Explicit Waits.

        :param locator: The ID used to locate the elements.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear.
        :return: A list of found elements, which can be empty if no elements are found.
        """
        return self.find_elements(By.ID, locator, seconds)

    def find_elements_by_name(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for multiple elements using the NAME method and implement Explicit Waits.

        :param locator: The NAME used to locate the elements.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear.
        :return: A list of found elements, which can be empty if no elements are found.
        """
        return self.find_elements(By.NAME, locator, seconds)

    def find_elements_by_tag(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for multiple elements using the TAG_NAME method and implement Explicit Waits.

        :param locator: The TAG_NAME used to locate the elements.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear.
        :return: A list of found elements, which can be empty if no elements are found.
        """
        return self.find_elements(By.TAG_NAME, locator, seconds)

    def find_elements_by_partial_link_text(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for multiple elements using the PARTIAL_LINK_TEXT method and implement Explicit Waits.

        :param locator: The PARTIAL_LINK_TEXT used to locate the elements.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear.
        :return: A list of found elements, which can be empty if no elements are found.
        """
        return self.find_elements(By.PARTIAL_LINK_TEXT, locator, seconds)

    def find_elements_by_link_text(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for multiple elements using the LINK_TEXT method and implement Explicit Waits.

        :param locator: The LINK_TEXT used to locate the elements.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear.
        :return: A list of found elements, which can be empty if no elements are found.
        """
        return self.find_elements(By.LINK_TEXT, locator, seconds)

    def find_elements_by_xpath(self, locator, seconds: int = LONG_WAIT_TIME):
        """ Search for multiple elements using the XPATH method and implement Explicit Waits.

        :param locator: The XPATH used to locate the elements.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear.
        :return: A list of found elements, which can be empty if no elements are found.
        """
        return self.find_elements(By.XPATH, locator, seconds)

    def count_elements(self, by_type, locator, seconds: int = LONG_WAIT_TIME):
        """ Obtain the count of matching elements within the specified maximum seconds: int = LONG_WAIT_TIME duration.

        :param by_type: The method used for locating the elements, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator, such as an ID, name, or XPath expression.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear (default is 5 seconds).
        :return: The count of matching elements or 0 if none are found.
        """
        try:
            return len(
                WebDriverWait(self.driver, seconds).until(
                    EC.visibility_of_all_elements_located((by_type, locator))))
        except TimeoutException:
            TimeoutException('Element was not found: {}'.format(locator))
        return 0

    def is_element_clickable(self, by_type, locator, seconds: int = LONG_WAIT_TIME):
        """ Retrieve the clickable status of the element within the specified maximum seconds period.

        :param by_type: The method used for locating the element, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator, such as an ID, name, or XPath expression.
        :param seconds: The maximum time, in seconds, to wait for the element to become clickable.
        :return: True if the element is clickable, False if not or if the element is not found.
        """
        try:
            WebDriverWait(self.driver, seconds).until(EC.element_to_be_clickable((by_type, locator)))
            return True
        except TimeoutException:
            Logger.debug("Element not clickable within specified time.")
            return False

    def is_element_enabled(self, by_type, locator, seconds: int = LONG_WAIT_TIME):
        """ Return the enabled status of the element within the specified maximum seconds: int = LONG_WAIT_TIME time.

        :param by_type: The method used for locating the element, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator, such as an ID, name, or XPath expression.
        :param seconds: The maximum time, in seconds, to wait for the element to appear.
        :return: True if the element is enabled, False if not or if the element is not found.
        """
        try:
            element = WebDriverWait(self.driver, seconds).until(
                EC.presence_of_element_located((by_type, locator))
            )
            return element.is_enabled()
        except TimeoutException:
            Logger.error(f"Element '{locator}' was not found or is not enabled.")
            return False

    def get_index_elements(self, by_type, locator, seconds: int = LONG_WAIT_TIME):
        """ Retrieve the index and a list of elements based on the provided locator.

        :param by_type: The method used for locating the elements, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator, such as an ID, name, or XPath expression.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear.
        :return: A list of tuples [(index, element), ...] or an empty list if no elements are found.
        """
        try:
            elements = WebDriverWait(self.driver, seconds).until(
                EC.visibility_of_all_elements_located((by_type, locator)))
            return [(index, element) for index, element in enumerate(elements)]
        except TimeoutException:
            Logger.debug(f"No elements found with locator '{locator}'.")
            return []

    def get_text_index_elements(self, text, by_type, locator, seconds: int = LONG_WAIT_TIME):
        """
       Obtain a list of index_element pairs based on the provided text that matches the text of the locator.

       :param text: The text to match within the element.
       :param by_type: The method used for locating the elements, e.g., 'id', 'name', 'xpath', etc.
       :param locator: The value of the locator, such as an ID, name, or XPath expression.
       :param seconds: The maximum time, in seconds, to wait for the elements to appear.
       :return: e.g. [(0, ele1), (1, ele2)] A list of index-element pairs [(index, element), ...]
       that contain the specified text.
       """
        index_elements = self.get_index_elements(by_type, locator, seconds)
        if index_elements:
            return [index_element for index_element in index_elements if text in index_element[1].text]
        else:
            Logger.debug("No elements were found that match the provided text in the locator.")
            return []

    def is_text_found(self, text, by_type, locator, seconds: int = LONG_WAIT_TIME):
        """ Return a boolean value based on the presence of the identified text.

        :param text: The text to search for within the elements.
        :param by_type: The method used for locating the elements, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator, such as an ID, name, or XPath expression.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear (default is 5 seconds).
        :return: True if the specified text is found in the identified elements, False otherwise.
        """
        return bool(self.get_text_index_elements(text, by_type, locator, seconds))

    def click(self, by_type, locator, delay_second: int = SHORT_WAIT_TIME, seconds: int = LONG_WAIT_TIME):
        """ Perform a click action on an element, scrolling if needed for visibility.

        :param by_type: The method used for locating the element, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator, such as an ID, name, or XPath expression.
        :param delay_second: The delay_second time, in seconds, before performing the click (default is 2 seconds).
        :param seconds: The maximum time, in seconds, to wait for the element to be clickable (default is 5 seconds).
        :return: None
        """
        try:
            WebDriverWait(self.driver, seconds).until(EC.element_to_be_clickable((by_type, locator)))
        except TimeoutException:
            Logger.debug('Element was not clickable: {}'.format(locator))
        el = self.find_element(by_type, locator)
        try:
            self.driver.execute_script("arguments[0].scrollIntoView();", el)
            el.click()
            Logger.debug("Clicked the element.")
            return
        except JavascriptException:
            fixed_wait(delay_second)
            Logger.debug("Couldn't execute JavaScript: scrollIntoView() for element: {} locator: {}".format(el, locator))

        el = self.find_element(by_type, locator)
        el.click()
        Logger.debug("Element found and clicked.")

    def click_no_scroll(self, locator, by_type=By.CSS_SELECTOR):
        """
        Click the element using its CSS selector without scrolling.

        :param locator: The CSS selector of the element.
        :param by_type: The method used for locating the element (default is CSS_SELECTOR).
        :return: None
        """
        try:
            el = self.find_element(by_type, locator)
            el.click()
            Logger.debug("Element clicked.")
        except WebDriverException as e:
            Logger.error(f"Error clicking element: {str(e)}")

    def click_text(self, text, by_type, locator, seconds: int = LONG_WAIT_TIME, index=0):
        """
        Retrieve a list of index-element pairs based on the provided text that matches the text of the locator,
        then click the element corresponding to the provided index.

        :param text: The text to search for within the elements.
        :param by_type: The method used for locating the elements, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator, such as an ID, name, or XPath expression.
        :param seconds: The maximum time, in seconds, to wait for the elements to appear.
        :param index: The index of the element to click (default is 0, the first element).
        :return: None
        """
        index_elements = self.get_text_index_elements(text, by_type, locator, seconds)
        try:
            element_to_click = index_elements[index][1]
            element_to_click.click()
            Logger.debug("Element found and clicked.")
        except IndexError:
            Logger.error(f"Index {index} out of bounds for elements matching text '{text}'.")

    def hover_over_element_and_click(self, element, by_type=None, locator=None, index: int = 0):
        """
        Hover over the element at index+1 and then click it.

        :param element: The element to hover over and click.
        :param by_type: The method used for locating additional elements, e.g., 'id', 'name', 'xpath', etc. (optional).
        :param locator: The value of the locator for additional elements (optional).
        :param index: The index of the additional element to click (default is 0).
        :return: None
        """
        try:
            actions = ActionChains(self.driver)
            actions.move_to_element(element)

            if by_type and locator:
                actions.perform()
                additional_elements = self.find_elements(by_type, locator)
                if 0 <= index < len(additional_elements):
                    additional_elements[index].click()
                    Logger.debug("Hovered over the element and clicked.")
                else:
                    Logger.error("Invalid index for additional elements.")
            else:
                actions.click(element).perform()
        except WebDriverException as e:
            Logger.error(f"Error during hover and click: {str(e)}")

    def hover_over_text_and_click(self, text, by_type, locator, click_type=None, click_locator=None, index=0,
                                  seconds: int = LONG_WAIT_TIME):
        """
        Retrieve a list of index_element pairs based on the provided text that matches the text of the locator.
        Then, hover over and click the element at index+1.

        :param text: The text to search for within the elements.
        :param by_type: The method used for locating the elements, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator, such as an ID, name, or XPath expression.
        :param click_type: The method used for locating the element to click,
        if different from the hover element (optional).
        :param click_locator: The value of the locator for the element to click (optional).
        :param index: The index of the element to click (default is 0).
        :param seconds: The maximum time, in seconds, to wait for the elements to appear (default is 7 seconds).
        :return: None
        """
        try:
            index_elements = self.get_text_index_elements(text, by_type, locator, seconds)

            if index_elements:
                index_element = index_elements[index] if index < len(index_elements) else index_elements[0]
                self.hover_over_element_and_click(index_element[1], click_type, click_locator)
            else:
                raise NoSuchElementException('Locator not found: {}'.format(locator))
        except WebDriverException as e:
            Logger.error(f"Error during hover and click: {str(e)}")

    def drag_and_drop(self, source_element, target_element):
        """
        Perform a drag-and-drop action from the source element to the target element.

        :param source_element: The element to drag from.
        :param target_element: The element to drop onto.
        :return: None
        """
        try:
            actions = ActionChains(self.driver)
            actions.drag_and_drop(source_element, target_element).perform()
        except Exception as e:
            Logger.error(f"Error during drag-and-drop: {str(e)}")

    def click_by_dict(self, dictionary):
        """
        Click the element using a dictionary of provided types.

        :param dictionary: A dictionary containing the locator type as the key and the locator value as the value.
        :return: None
        """
        by_type = next(iter(dictionary))
        locator = dictionary.get(by_type)
        self.click(by_type, locator)

    def click_by_css(self, locator, by_type=By.CSS_SELECTOR):
        """
        Click the element using its CSS selector.

        :param locator: The CSS selector of the element.
        :param by_type: The method used for locating the element (default is CSS_SELECTOR).
        :return: None
        """
        self.click(by_type, locator)

    def type_without_click(self, text, by_type, locator):
        """
        Type text into an input field identified by its locator without performing a click action.

        :param text: The text to type into the input field.
        :param by_type: The method used for locating the input field, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator for the input field.
        :return: None
        """
        el = self.find_element(by_type, locator)
        el.send_keys(text)

    def select(self, option, by_type, locator):
        """
       Select an option from a dropdown element based on its visible text.

       :param option: The visible text of the option to select.
       :param by_type: The method used for locating the dropdown element, e.g., 'id', 'name', 'xpath', etc.
       :param locator: The value of the locator for the dropdown element.
       :return: None
       """
        _select = Select(self.find_element(by_type, locator))
        _select.select_by_visible_text(option)

    def select_by_dict(self, option, dictionary):
        """
        Select an option from a dropdown element based on its visible text
        using a dictionary of provided types.

        :param option: The visible text of the option to select.
        :param dictionary: A dictionary containing the locator type as the key and the locator value as the value.
        :return: None
        """
        by_type = next(iter(dictionary))
        locator = dictionary.get(by_type)
        _select = Select(self.find_element(by_type, locator))
        _select.select_by_visible_text(option)

    def type_text(self, text, by_type, locator):
        """
        Type text into an input field identified by its locator.

        :param text: The text to type into the input field.
        :param by_type: The method used for locating the input field, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator for the input field.
        :return: None
        """
        el = self.find_element(by_type, locator)
        el.click()
        el.send_keys(text)

    def type_text_dict(self, text, dictionary):
        """
        Type text into an input field using a dictionary of provided types.

        :param text: The text to type into the input field.
        :param dictionary: A dictionary containing the locator type as the key and the locator value as the value.
        :return: None
        """
        by_type = next(iter(dictionary))
        locator = dictionary.get(by_type)
        self.type_without_click(text, by_type, locator)

    def clear_text(self, by_type, locator, seconds: int = LONG_WAIT_TIME):
        """
        Clear the text from an input field identified by its locator.

        :param by_type: The method used for locating the input field, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator for the input field.
        :param seconds: int = LONG_WAIT_TIME: The maximum time, in seconds, to wait for the element to appear.
        :return: None
        """
        el = self.find_element(by_type, locator, seconds)
        el.click()
        el.clear()

    def type_text_press_enter(self, text, by_type, locator):
        """
        Type text into an input field identified by its locator and press the Enter key.

        :param text: The text to type into the input field.
        :param by_type: The method used for locating the input field, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator for the input field.
        :return: None
        """
        input_field = self.find_element(by_type, locator)
        input_field.send_keys(text)
        input_field.send_keys(Keys.RETURN)

    def clear_input_box_press_enter(self, by_type, locator, delay_second: int = SHORT_WAIT_TIME):
        """
        Clear the content of an input box identified by its locator and press the Enter key.

        :param by_type: The method used for locating the input box, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator for the input box.
        :param delay_second: The delay_second time, in seconds, before performing the click.
        :return: None
        """
        ele = self.find_element(by_type, locator)
        ActionChains(self.driver).double_click(ele).perform()
        ele.send_keys(Keys.DELETE)
        ele.send_keys(Keys.ENTER)
        fixed_wait(delay_second)

    def get_text_from_element(self, page_element):
        """
        Get the text content from a given element.

        :param page_element: The element from which to retrieve the text.
        :return: The text content of the element.
        """
        self.driver.execute_script("arguments[0].scrollIntoView();", page_element)
        return page_element.text

    def get_text(self, by_type, locator):
        """
        Get the text content from an element identified by its locator.

        :param by_type: The method used for locating the element, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator for the element.
        :return: The text content of the element.
        """
        el = self.find_element(by_type, locator)
        return self.get_text_from_element(el)

    def get_text_from_page(self):
        """
        Get the text content from the entire page.

        :return: The text content of the page.
        """
        return self.get_text(By.TAG_NAME, "body")

    def get_attribute(self, by_type, locator, attribute):
        """
        Get the value of a specified attribute from an element identified by its locator.

        :param by_type: The method used for locating the element, e.g., 'id', 'name', 'xpath', etc.
        :param locator: The value of the locator for the element.
        :param attribute: The name of the attribute whose value is to be retrieved.
        :return: The value of the specified attribute.
        """
        el = self.find_element(by_type, locator)
        return el.get_attribute(attribute)

    def get_child_elements_by_css(self, by_type, parent_locator, child_css):
        """
        Get child elements of a parent element identified by its locator using a CSS selector.

        :param by_type: The method used for locating the parent element, e.g., 'id', 'name', 'xpath', etc.
        :param parent_locator: The value of the locator for the parent element.
        :param child_css: The CSS selector for the child elements.
        :return: A list of child elements matching the CSS selector.
        """
        try:
            parent_element = self.find_element(by_type, parent_locator)
            return parent_element.find_elements(By.CSS_SELECTOR, child_css)
        except NoSuchElementException:
            Logger.error("Element not found.")
            return []

    def switch_window(self):
        """
        Switch to a different window handle.

        :return: None
        """
        fixed_wait()
        handles = self.driver.window_handles
        for handle in handles:
            if handle != self.driver.current_window_handle:
                self.driver.switch_to.window(handle)
            else:
                raise NoSuchWindowException("No target window handle found.")

    def get_title(self):
        """Get the title of the current page.

        :return: A string containing the title of the current page.
        """
        try:
            page_title = self.driver.title
            Logger.debug(f"Page Title: {page_title}")
            return page_title
        except Exception as e:
            Logger.error(f"Error getting page title: {str(e)}")
            return None

    def wait_for_title(self, title, seconds: int = LONG_WAIT_TIME):
        """
        Wait for the browser window's title to contain the specified title text.

        :param title: The title text to wait for.
        :param seconds: The maximum time, in seconds, to wait for the title.
        :return: None
        """
        try:
            WebDriverWait(self.driver, seconds).until(EC.title_contains(title))
        except TimeoutException:
            pass

    def wait_for_link(self, link_text, seconds: int = LONG_WAIT_TIME):
        """
        Wait for a link with the specified link text to appear in the page.

        :param link_text: The link text to wait for.
        :param seconds: The maximum time, in seconds, to wait for the link.
        :return: None
        """
        try:
            WebDriverWait(self.driver, seconds).until(EC.presence_of_element_located((By.LINK_TEXT, link_text)))
        except TimeoutException:
            pass

    def find_button_equal_text_click(self, button_text, css_selector='button'):
        """
        Find and click a button with the specified exact text and CSS selector.

        :param button_text: The exact text of the button to find and click.
        :param css_selector: The CSS selector for locating the buttons.
        :return: None
        """
        action_buttons = self.find_elements(By.CSS_SELECTOR, css_selector)
        for button in action_buttons:
            if button_text == button.text:
                button.click()
                fixed_wait(1)
                break

    def find_button_contain_text_click(self, button_text, css_selector='button'):
        """
        Find and click a button containing the specified text and matching the CSS selector.

        :param button_text: The text to search for in the button's text content.
        :param css_selector: The CSS selector for locating the buttons.
        :return: None
        """
        action_buttons = self.find_elements(By.CSS_SELECTOR, css_selector)
        for button in action_buttons:
            if button_text in button.text:
                button.click()
                fixed_wait(1)
                break

    def select_radio_equal_text_click(self, radio_text, css_selector):
        """
        Select a radio button when its label text is equal to the expected text.

        :param radio_text: The expected label text of the radio button.
        :param css_selector: The CSS selector for locating the radio button labels.
        :return: None
        """
        element_options = self.find_elements(By.CSS_SELECTOR, css_selector)
        for ele in element_options:
            if radio_text == ele.text:
                radio_ele = ele.find_element(By.CSS_SELECTOR, 'input[type="radio"]')
                radio_ele.click()
                fixed_wait()
                break

    def find_row_contain_text_click_button(self, row_text, button_text, row_css, button_css):
        """
        Find a table row containing specified text, locate a button in that row, and click the button.

        :param row_text: The text to search for in the table row.
        :param button_text: The text of the button within the row to click.
        :param row_css: The CSS selector for locating table rows.
        :param button_css: The CSS selector for locating buttons within the rows.
        :return: None
        """
        action_rows = self.find_elements(By.CSS_SELECTOR, row_css)
        for row in action_rows:
            if row_text in row.text:
                action_buttons = row.find_elements(By.CSS_SELECTOR, button_css)
                for button in action_buttons:
                    if button_text in button.text:
                        button.click()
                        fixed_wait()
                        return

    def find_row_contain_text_return_cell_element(self, row_text, row_css, cell_css):
        """
        Find a table row containing specified text, locate a cell in that row, and return the cell element.

        :param row_text: The text to search for in the table row.
        :param row_css: The CSS selector for locating table rows.
        :param cell_css: The CSS selector for locating cells within the rows.
        :return: The WebElement representing the target cell, or None if not found.
        """
        element_rows = self.find_elements(By.CSS_SELECTOR, row_css)
        if element_rows is None:
            return None
        for row in element_rows:
            if row_text in row.text:
                target_cell = row.find_element(By.CSS_SELECTOR, cell_css)
                return target_cell
        return None

    def find_row_contain_text_return_cell_text(self, row_text, row_css, cell_css):
        """
        Find a table row containing specified text, locate a cell in that row, and return the text content of the cell.

        :param row_text: The text to search for in the table row.
        :param row_css: The CSS selector for locating table rows.
        :param cell_css: The CSS selector for locating cells within the rows.
        :return: The text content of the target cell, or None if not found.
        """
        element_rows = self.find_elements(By.CSS_SELECTOR, row_css)
        if element_rows is None:
            return None
        for row in element_rows:
            if row_text in row.text:
                target_cell = row.find_element(By.CSS_SELECTOR, cell_css)
                return target_cell.text
        return None

    def find_row_contain_text_click_element(self, row_text, row_css, element_css, n=1):
        """
        Find a table row containing specified text, locate an element in that row, and click it.

        :param row_text: The text to search for in the table row.
        :param row_css: The CSS selector for locating table rows.
        :param element_css: The CSS selector for locating the elements within the rows.
        :param n: The number of elements to click (default is 1).
        :return: None
        """
        ele_rows = self.find_elements(By.CSS_SELECTOR, row_css)
        flag = 0
        for row in ele_rows:
            if row_text in row.text:
                flag += 1
                action_element = row.find_element(By.CSS_SELECTOR, element_css)
                try:
                    WebDriverWait(self.driver, 30).until(EC.element_to_be_clickable((By.CSS_SELECTOR, element_css)))
                except TimeoutException:
                    Logger.debug(f"Element {row.text} never became clickable")
                self.driver.execute_script("arguments[0].scrollIntoView();", action_element)
                action_element.click()
                fixed_wait(1)
                if n is not None and n >= flag:
                    return

    def find_row_contain_two_texts_click(self, row_text, another_text, row_css, element_css, n=1):
        """
        Compare values in two columns of a table and click an element if the conditions are met.

        :param row_text: Text to search for in the table row.
        :param another_text: Another text to search for in the table row.
        :param row_css: CSS selector for locating table rows.
        :param element_css: CSS selector for locating the element within the rows to click.
        :param n: Number of elements to click (default is 1).
        :return: Number of elements clicked.
        """
        ele_rows = self.find_elements(By.CSS_SELECTOR, row_css)
        flag = 0
        for row in ele_rows:
            if row_text.lower() in row.text.lower() and another_text.lower() in row.text.lower():
                flag += 1
                action_element = row.find_element(By.CSS_SELECTOR, element_css)
                action_element.click()
                fixed_wait(1)
                if n is not None and n >= flag:
                    return flag
        return flag

    def find_contain_text_hover_click(self, text, css_selector, hover_css_selector,
                                      delay_second: int = SHORT_WAIT_TIME):
        """
        Find a row containing the specified text, hover over the specified element, and click it.

        :param text: Text to search for in the table row.
        :param css_selector: CSS selector for locating table rows.
        :param hover_css_selector: CSS selector for locating the element to hover over.
        :param delay_second: The delay_second time, in seconds, before performing the click.
        :return: True if successful, False otherwise.
        """
        rows = self.find_elements(By.CSS_SELECTOR, css_selector)
        for row in rows:
            if text in row.text:
                view_button = row.find_element(By.CSS_SELECTOR, hover_css_selector)
                hover = ActionChains(self.driver).move_to_element(view_button)
                hover.perform()
                view_button.click()
                fixed_wait(delay_second)
                return True
        return False

    def find_contain_text_hover_click_another(self, text, css_selector, hover_css_selector, click_css_selector,
                                              seconds: int = SHORT_WAIT_TIME):
        """
        Find a row containing the specified text, hover over a specified element, and click another element.

        :param text: Text to search for in the table row.
        :param css_selector: CSS selector for locating table rows.
        :param hover_css_selector: CSS selector for locating the element to hover over.
        :param click_css_selector: CSS selector for locating the element to click after hovering.
        :param seconds: The seconds time, in seconds, before performing the click.
        :return: None
        """
        rows = self.find_elements(By.CSS_SELECTOR, css_selector)
        for row in rows:
            if text in row.text:
                view_button = row.find_element(By.CSS_SELECTOR, hover_css_selector)
                hover = ActionChains(self.driver).move_to_element(view_button)
                hover.perform()
                fixed_wait(seconds)
                row.find_element(By.CSS_SELECTOR, click_css_selector).click()
                fixed_wait(seconds)
                break

    def find_contain_text_type_text(self, search_text, css_selector, type_text_css_selector, text_to_type,
                                    seconds: int = SHORT_WAIT_TIME):
        """
        Find a row containing the specified text, locate an input element, and type text into it.

        :param search_text: Text to search for in the table row.
        :param css_selector: CSS selector for locating table rows.
        :param type_text_css_selector: CSS selector for locating the input element.
        :param text_to_type: Text to type into the input element.
        :param seconds: The seconds time, in seconds, before performing the click.
        :return: True if the text is found and typed, False otherwise.
        """
        elems = self.find_elements(By.CSS_SELECTOR, css_selector)
        for elem in elems:
            if search_text in elem.text:
                type_text_elem = elem.find_element(By.CSS_SELECTOR, type_text_css_selector)
                self.driver.execute_script("arguments[0].scrollIntoView();", type_text_elem)
                type_text_elem.click()
                type_text_elem.clear()
                type_text_elem.send_keys(text_to_type)
                fixed_wait(seconds)
                return True
        return False

    def click_presentation_contain_role_click(self, ul_role, role_name, seconds: int = SHORT_WAIT_TIME):
        """
        Click an item within a presentation list based on a specific role name.

        :param ul_role: The role attribute of the <ul> element containing the list.
        :param role_name: The role name to be matched within the list.
        :param seconds: The seconds time, in seconds, before performing the click.
        :return: None
        """
        rows = self.find_elements(By.CSS_SELECTOR, f'div[role="presentation"] ul[role="{ul_role}"] li')
        for row in rows:
            if role_name in row.text:
                row.click()
                break
        fixed_wait(seconds)

    def close_popup_banner(self):
        """
        Close the popup banner using a matched CSS selector pattern.

        :return: None
        """
        dialog_button = self.find_element(By.CSS_SELECTOR, 'button[id*="pendo-button"]')
        if dialog_button is None:
            dialog_button = self.find_element(By.CSS_SELECTOR, 'button[id*="pendo-close"]')
        if dialog_button is not None:
            dialog_button.click()

    def close_pendo_banners(self, seconds: int = SHORT_WAIT_TIME):
        """Close all popup banners using a matched CSS selector pattern.

        :return: None
        """
        try:
            dialog_buttons = self.find_elements(By.CSS_SELECTOR, 'button[id^="pendo-close-guide"]')
            Logger.debug(f"Found {len(dialog_buttons)} banner(s) to close.")
            for index, button in enumerate(dialog_buttons, start=1):
                try:
                    button.click()
                    Logger.debug(f"Closed banner {index}/{len(dialog_buttons)}")
                    fixed_wait(seconds)
                except WebDriverException as e:
                    Logger.error(f"Error clicking banner close button ({index}/{len(dialog_buttons)}): {str(e)}")
        except WebDriverException as e:
            Logger.error(f"Error finding banner close buttons: {str(e)}")
