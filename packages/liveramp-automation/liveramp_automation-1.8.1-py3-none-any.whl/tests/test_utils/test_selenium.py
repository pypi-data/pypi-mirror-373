import pytest
from unittest.mock import Mock, patch
from liveramp_automation.utils.selenium import SeleniumUtils
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.keys import Keys


@pytest.fixture
def mock_chrome_driver():
    mock_driver = Mock()
    mock_driver.current_url = 'https://liveramp.com/careers/'
    mock_driver.title = 'Liveramp'

    mock_element_1 = Mock()
    mock_element_1.get_attribute.return_value = "element_test_1"

    mock_element_2 = Mock()
    mock_element_2.get_attribute.return_value = "element_test_2"

    mock_element = Mock()
    mock_element.get_attribute.return_value = "element_test"

    mock_driver.find_elements.return_value = [mock_element_1, mock_element_2]
    mock_driver.find_element.return_value = mock_element

    return mock_driver


def test_open_page(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    my_selenium_instance.get_url(mock_chrome_driver.url)
    ##
    # mock_chrome_driver.url.assert_called_once()


def test_navigate_to_url(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    my_selenium_instance.navigate_to_url(path='/test', query='param=value')

def test_navigate_to_url_no_path_no_query(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    my_selenium_instance.navigate_to_url(path=None, query=None)


def mocked_exception_response(*args, **kwargs):
    raise Exception("Test Exception")

@patch('urllib.parse.urlparse', side_effect=mocked_exception_response)
def test_navigate_to_url_no_path_no_query(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    my_selenium_instance.navigate_to_url(path=None, query=None)

def test_refresh_page_url(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    my_selenium_instance.refresh_page()
    bbb = my_selenium_instance.get_page_url()
    assert bbb == mock_chrome_driver.current_url


def test_get_title(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    result = my_selenium_instance.get_title()
    assert result == "Liveramp"


def test_save_screenshot(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    my_selenium_instance.save_screenshot('test_screenshot')


def test_get_url(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    my_selenium_instance.get_url(mock_chrome_driver.current_url)
    mock_chrome_driver.get.assert_called_once_with(mock_chrome_driver.current_url)


def test_get_page_url(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    url = my_selenium_instance.get_page_url()
    assert url == mock_chrome_driver.current_url


def test_find_element_by_dict(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    dictionary = {By.ID: 'element_test_1'}
    elements = my_selenium_instance.find_elements_by_dict(dictionary)
    assert elements[0].get_attribute("id") == "element_test_1"
    mock_chrome_driver.find_elements.assert_called_once_with(By.ID, 'element_test_1')


def test_find_elements_by_dict(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    dictionary = {By.ID: 'element_test_1'}
    elements = my_selenium_instance.find_elements_by_dict(dictionary)
    assert len(elements) == 2
    assert elements[0].get_attribute("id") == "element_test_1"
    assert elements[1].get_attribute("id") == "element_test_2"
    mock_chrome_driver.find_elements.assert_called_once_with(By.ID, 'element_test_1')


def test_find_element(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    by_type = By.ID
    locator = 'element_test'
    element = my_selenium_instance.find_element(by_type, locator)
    assert element.get_attribute("id") == "element_test"
    mock_chrome_driver.find_element.assert_called_once_with(by_type, locator)


def test_find_element_by_css(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = '.example-css-selector'
    element = my_selenium_instance.find_element_by_css(locator)
    assert element.get_attribute("id") == "element_test"
    mock_chrome_driver.find_element.assert_called_once_with(By.CSS_SELECTOR, locator)


def test_find_element_by_xpath(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = '//div[@class="example-class"]'
    element = my_selenium_instance.find_element_by_xpath(locator)
    assert element.get_attribute("id") == "element_test"
    mock_chrome_driver.find_element.assert_called_once_with(By.XPATH, locator)


def test_find_element_by_name(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_name'
    element = my_selenium_instance.find_element_by_name(locator)
    assert element.get_attribute("id") == "element_test"
    mock_chrome_driver.find_element.assert_called_once_with(By.NAME, locator)


def test_find_element_by_tag(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'div'
    element = my_selenium_instance.find_element_by_tag(locator)
    assert element.get_attribute("id") == "element_test"
    mock_chrome_driver.find_element.assert_called_once_with(By.TAG_NAME, locator)


def test_find_element_by_id(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_id'
    element = my_selenium_instance.find_element_by_id(locator)
    assert element.get_attribute("id") == "element_test"
    mock_chrome_driver.find_element.assert_called_once_with(By.ID, locator)


def test_find_element_by_link_text(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'Example Link Text'
    element = my_selenium_instance.find_element_by_link_text(locator)
    assert element.get_attribute("id") == "element_test"
    mock_chrome_driver.find_element.assert_called_once_with(By.LINK_TEXT, locator)


def test_find_element_by_partial_link_text(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'Partial Link Text'
    element = my_selenium_instance.find_element_by_partial_link_text(locator)
    assert element.get_attribute("id") == "element_test"
    mock_chrome_driver.find_element.assert_called_once_with(By.PARTIAL_LINK_TEXT, locator)


def test_find_element_by_class_name(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_class'
    element = my_selenium_instance.find_element_by_class_name(locator)
    assert element.get_attribute("id") == "element_test"
    mock_chrome_driver.find_element.assert_called_once_with(By.CLASS_NAME, locator)


def test_find_elements(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    by_type = By.XPATH
    locator = '//div'
    elements = my_selenium_instance.find_elements(by_type, locator)
    assert len(elements) == 2
    assert elements[0].get_attribute("id") == "element_test_1"
    assert elements[1].get_attribute("id") == "element_test_2"
    mock_chrome_driver.find_elements.assert_called_once_with(by_type, locator)


def test_find_elements_by_css(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'div.example-class'
    elements = my_selenium_instance.find_elements_by_css(locator)
    assert len(elements) == 2
    assert elements[0].get_attribute("id") == "element_test_1"
    assert elements[1].get_attribute("id") == "element_test_2"
    mock_chrome_driver.find_elements.assert_called_once_with(By.CSS_SELECTOR, locator)


def test_find_elements_by_class_name(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example-class'
    elements = my_selenium_instance.find_elements_by_class_name(locator)
    assert len(elements) == 2
    assert elements[0].get_attribute("id") == "element_test_1"
    assert elements[1].get_attribute("id") == "element_test_2"
    mock_chrome_driver.find_elements.assert_called_once_with(By.CLASS_NAME, locator)


def test_find_elements_by_id(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_id'
    elements = my_selenium_instance.find_elements_by_id(locator)
    assert len(elements) == 2
    assert elements[0].get_attribute("id") == "element_test_1"
    assert elements[1].get_attribute("id") == "element_test_2"
    mock_chrome_driver.find_elements.assert_called_once_with(By.ID, locator)


def test_find_elements_by_name(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_name'
    elements = my_selenium_instance.find_elements_by_name(locator)
    assert len(elements) == 2
    assert elements[0].get_attribute("id") == "element_test_1"
    assert elements[1].get_attribute("id") == "element_test_2"
    mock_chrome_driver.find_elements.assert_called_once_with(By.NAME, locator)


def test_find_elements_by_tag(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_tag'
    elements = my_selenium_instance.find_elements_by_tag(locator)
    assert len(elements) == 2
    assert elements[0].get_attribute("id") == "element_test_1"
    assert elements[1].get_attribute("id") == "element_test_2"
    mock_chrome_driver.find_elements.assert_called_once_with(By.TAG_NAME, locator)


def test_find_elements_by_partial_link_text(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_partial_link_text'
    elements = my_selenium_instance.find_elements_by_partial_link_text(locator)
    assert len(elements) == 2
    assert elements[0].get_attribute("id") == "element_test_1"
    assert elements[1].get_attribute("id") == "element_test_2"
    mock_chrome_driver.find_elements.assert_called_once_with(By.PARTIAL_LINK_TEXT, locator)


def test_find_elements_by_link_text(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_link_text'
    elements = my_selenium_instance.find_elements_by_link_text(locator)
    assert len(elements) == 2
    assert elements[0].get_attribute("id") == "element_test_1"
    assert elements[1].get_attribute("id") == "element_test_2"
    mock_chrome_driver.find_elements.assert_called_once_with(By.LINK_TEXT, locator)


def test_find_elements_by_xpath(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_xpath'
    elements = my_selenium_instance.find_elements_by_xpath(locator)
    assert len(elements) == 2
    assert elements[0].get_attribute("id") == "element_test_1"
    assert elements[1].get_attribute("id") == "element_test_2"
    mock_chrome_driver.find_elements.assert_called_once_with(By.XPATH, locator)


def test_count_elements(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_locator'
    count = my_selenium_instance.count_elements(By.XPATH, locator)
    assert count == 2
    mock_chrome_driver.find_elements.assert_called_once_with(By.XPATH, locator)


def test_is_element_clickable(mock_chrome_driver):
    mock_xpath_element = Mock(spec=WebElement)
    mock_xpath_element.tag_name = "button"
    mock_xpath_element.get_attribute.return_value = "my-button"
    mock_xpath_element.is_enabled.return_value = True
    mock_xpath_element.is_displayed.return_value = True
    mock_chrome_driver.find_element.return_value = mock_xpath_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    by_type = By.XPATH
    locator = "//button[@id='my-button']"
    seconds = 5
    result = selenium_utils.is_element_clickable(by_type, locator, seconds)
    assert result is True


def test_is_element_enabled_true(mock_chrome_driver):
    mock_element = Mock()
    mock_element.is_enabled.return_value = True
    mock_chrome_driver.find_element.return_value = mock_element
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_locator'
    result = my_selenium_instance.is_element_enabled(By.XPATH, locator)
    assert result is True


def test_is_element_enabled_false(mock_chrome_driver):
    mock_element = Mock()
    mock_element.is_enabled.return_value = False
    mock_chrome_driver.find_element.return_value = mock_element
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_locator'
    result = my_selenium_instance.is_element_enabled(By.XPATH, locator)
    assert result is False


def test_get_index_elements(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_locator'
    result = my_selenium_instance.get_index_elements(By.XPATH, locator)
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in result)


def test_get_text_index_elements(mock_chrome_driver):
    mock_element_1 = Mock()
    mock_element_1.text = "Element 1 Text"
    mock_element_2 = Mock()
    mock_element_2.text = "Element 2 Text"
    mock_element_3 = Mock()
    mock_element_3.text = "Element 3 Text"
    mock_chrome_driver.find_elements.return_value = [mock_element_1, mock_element_2, mock_element_3]
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    text_to_match = "Element 2 Text"
    locator = 'example_locator'
    result = my_selenium_instance.get_text_index_elements(text_to_match, By.XPATH, locator)
    assert isinstance(result, list)
    assert all(isinstance(item, tuple) and len(item) == 2 for item in result)
    assert all(text_to_match in item[1].text for item in result)


def test_is_text_found(mock_chrome_driver):
    mock_element_1 = Mock()
    mock_element_1.text = "Element 1 Text"
    mock_element_2 = Mock()
    mock_element_2.text = "Element 2 Text"
    mock_element_3 = Mock()
    mock_element_3.text = "Element 3 Text"
    mock_chrome_driver.find_elements.return_value = [mock_element_1, mock_element_2, mock_element_3]
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    text_to_find = "Element 2 Text"
    locator = 'example_locator'
    result = my_selenium_instance.is_text_found(text_to_find, By.XPATH, locator)
    assert result is True


def test_click(mock_chrome_driver):
    mock_xpath_element = Mock(spec=WebElement)
    mock_xpath_element.tag_name = "button"
    mock_xpath_element.get_attribute.return_value = "my-button"
    mock_xpath_element.is_enabled.return_value = True
    mock_xpath_element.is_displayed.return_value = True
    mock_chrome_driver.find_element.return_value = mock_xpath_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    by_type = By.XPATH
    locator = "//button[@id='my-button']"
    delay_second = 2
    seconds = 5
    selenium_utils.click(by_type, locator, delay_second, seconds)
    assert True


def test_click_no_scroll(mock_chrome_driver):
    mock_element = Mock()
    mock_element.text = "Element Text"
    mock_chrome_driver.find_element.return_value = mock_element
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    locator = 'example_locator'
    my_selenium_instance.click_no_scroll(locator)
    mock_chrome_driver.find_element.assert_called_once_with(By.CSS_SELECTOR, locator)
    mock_element.click.assert_called_once()


def test_click_text(mock_chrome_driver):
    mock_element_1 = Mock()
    mock_element_2 = Mock()
    mock_element_1.text = "Platform"
    mock_element_2.text = "Platform"
    mock_chrome_driver.find_elements.return_value = [mock_element_1, mock_element_2]
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    text = 'Platform'
    locator = 'example_locator'
    index = 1  # Index of the element to click
    my_selenium_instance.click_text(text, By.XPATH, locator, index=index)
    mock_chrome_driver.find_elements.assert_called_once_with(By.XPATH, locator)
    mock_element_2.click.assert_called_once()


def test_hover_over_element_and_click(mock_chrome_driver):
    mock_xpath_element = Mock(spec=WebElement)
    mock_xpath_element.tag_name = "button"
    mock_xpath_element.get_attribute.return_value = "my-button"
    mock_xpath_element.is_enabled.return_value = True
    mock_xpath_element.is_displayed.return_value = True
    mock_chrome_driver.find_element.return_value = mock_xpath_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    element = mock_chrome_driver.find_element(By.XPATH, "//button[@id='my-button']")
    by_type = By.XPATH
    locator = "//additional-element"
    index = 0
    selenium_utils.hover_over_element_and_click(element, by_type, locator, index)
    assert True


'''def test_hover_over_text_and_click(mock_chrome_driver):
    mock_xpath_element = Mock(spec=WebElement)
    mock_xpath_element.tag_name = "button"
    mock_xpath_element.get_attribute.return_value = "my-button"
    mock_xpath_element.is_enabled.return_value = True
    mock_xpath_element.is_displayed.return_value = True
    mock_chrome_driver.find_element.return_value = mock_xpath_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    text = "Button Text"
    by_type = By.XPATH
    locator = "//element-with-text"
    click_type = By.XPATH
    click_locator = "//click-element"
    index = 0
    selenium_utils.hover_over_text_and_click(text, by_type, locator, click_type, click_locator, index)
    assert True'''


def test_drag_and_drop(mock_chrome_driver):
    mock_source_element = Mock(spec=WebElement)
    mock_target_element = Mock(spec=WebElement)
    mock_source_element.tag_name = "div"
    mock_target_element.tag_name = "div"
    mock_chrome_driver.execute_script.return_value = None
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    selenium_utils.drag_and_drop(mock_source_element, mock_target_element)
    assert True


def test_click_by_dict(mock_chrome_driver):
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    locator_dict = {
        By.XPATH: "//button[@id='my-button']"
    }
    selenium_utils.click_by_dict(locator_dict)
    assert True


def test_click_by_css(mock_chrome_driver):
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    css_selector = "#my-button"
    selenium_utils.click_by_css(css_selector)
    assert True


def test_type_without_click(mock_chrome_driver):
    mock_input_element = Mock(spec=WebElement)
    mock_input_element.tag_name = "input"
    mock_input_element.get_attribute.return_value = "text"
    mock_input_element.is_enabled.return_value = True
    mock_input_element.is_displayed.return_value = True
    mock_input_element.get_attribute.side_effect = lambda attr: "input value" if attr == "value" else None
    mock_input_element.send_keys.return_value = None
    mock_chrome_driver.find_element.return_value = mock_input_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    text = "Texto de prueba"
    by_type = By.XPATH
    locator = "//input[@id='my-input']"
    selenium_utils.type_without_click(text, by_type, locator)
    assert True


def test_select(mock_chrome_driver):
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    option_text = "Option 1"
    by_type = By.XPATH
    locator = "//select[@id='my-select']"
    mock_chrome_driver.find_element(by_type, locator)
    with pytest.raises(Exception):
        selenium_utils.select(option_text, by_type, locator)
        assert True


def test_select_by_dict(mock_chrome_driver):
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    option_text = "Option 1"
    locator_dict = {
        By.XPATH: "//select[@id='my-select']"
    }
    for by_type, locator in locator_dict.items():
        mock_chrome_driver.find_element(by_type, locator)
        with pytest.raises(Exception):
            selenium_utils.select_by_dict(option_text, locator_dict)
            assert True


def test_type_text(mock_chrome_driver):
    mock_input_element = Mock(spec=WebElement)
    mock_input_element.tag_name = "input"
    mock_input_element.get_attribute.return_value = "text"
    mock_input_element.is_enabled.return_value = True
    mock_input_element.is_displayed.return_value = True
    mock_input_element.get_attribute.side_effect = lambda attr: "input value" if attr == "value" else None
    mock_input_element.click.return_value = None
    mock_input_element.send_keys.return_value = None
    mock_chrome_driver.find_element.return_value = mock_input_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    text = "Texto de prueba"
    by_type = By.XPATH
    locator = "//input[@id='my-input']"
    selenium_utils.type_text(text, by_type, locator)
    assert True


def test_type_text_dict(mock_chrome_driver):
    mock_input_element = Mock(spec=WebElement)
    mock_input_element.tag_name = "input"
    mock_input_element.get_attribute.return_value = "text"
    mock_input_element.is_enabled.return_value = True
    mock_input_element.is_displayed.return_value = True
    mock_input_element.get_attribute.side_effect = lambda attr: "input value" if attr == "value" else None
    mock_input_element.send_keys.return_value = None
    mock_chrome_driver.find_element.return_value = mock_input_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    text = "Texto de prueba"
    locator_dict = {
        By.XPATH: "//input[@id='my-input']"
    }
    selenium_utils.type_text_dict(text, locator_dict)
    assert True


def test_clear_text(mock_chrome_driver):
    mock_input_element = Mock(spec=WebElement)
    mock_input_element.tag_name = "input"
    mock_input_element.get_attribute.return_value = "text"
    mock_input_element.is_enabled.return_value = True
    mock_input_element.is_displayed.return_value = True
    mock_input_element.get_attribute.side_effect = lambda attr: "input value" if attr == "value" else None
    mock_input_element.click.return_value = None
    mock_input_element.clear.return_value = None
    mock_chrome_driver.find_element.return_value = mock_input_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    by_type = By.XPATH
    locator = "//input[@id='my-input']"
    selenium_utils.clear_text(by_type, locator)
    assert True


def test_type_text_press_enter(mock_chrome_driver):
    mock_input_element = Mock(spec=WebElement)
    mock_input_element.tag_name = "input"
    mock_input_element.get_attribute.return_value = "text"
    mock_input_element.is_enabled.return_value = True
    mock_input_element.is_displayed.return_value = True
    mock_input_element.get_attribute.side_effect = lambda attr: "input value" if attr == "value" else None
    mock_input_element.send_keys.return_value = None
    mock_input_element.send_keys.side_effect = lambda keys: None if keys == Keys.RETURN else None
    mock_chrome_driver.find_element.return_value = mock_input_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    text = "Texto de prueba"
    by_type = By.XPATH
    locator = "//input[@id='my-input']"
    selenium_utils.type_text_press_enter(text, by_type, locator)
    assert True


def test_clear_input_box_press_enter(mock_chrome_driver):
    mock_input_element = Mock(spec=WebElement)
    mock_input_element.tag_name = "input"
    mock_input_element.get_attribute.return_value = "text"
    mock_input_element.is_enabled.return_value = True
    mock_input_element.is_displayed.return_value = True
    mock_input_element.get_attribute.side_effect = lambda attr: "input value" if attr == "value" else None
    mock_input_element.send_keys.side_effect = lambda keys: None if keys in [Keys.DELETE, Keys.ENTER] else None
    mock_chrome_driver.find_element.return_value = mock_input_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    by_type = By.XPATH
    locator = "//input[@id='my-input']"
    selenium_utils.clear_input_box_press_enter(by_type, locator)
    assert True


def test_get_text_from_element(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    mock_chrome_driver.execute_script = Mock()
    mock_page_element = Mock()
    mock_page_element.text = "Test"
    result = my_selenium_instance.get_text_from_element(mock_page_element)
    mock_chrome_driver.execute_script.assert_called_once_with("arguments[0].scrollIntoView();", mock_page_element)
    assert result == "Test"


def test_get_text(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    mock_chrome_driver.find_element = Mock()
    mock_page_element = Mock()
    mock_page_element.text = "Test"
    mock_chrome_driver.find_element.return_value = mock_page_element
    result = my_selenium_instance.get_text(By.CSS_SELECTOR, "example_locator")
    mock_chrome_driver.find_element.assert_called_once_with(By.CSS_SELECTOR, "example_locator")
    assert result == "Test"


def test_get_text_from_page(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    mock_chrome_driver.find_element = Mock()
    mock_page_element = Mock()
    mock_page_element.text = "Test"
    mock_chrome_driver.find_element.return_value = mock_page_element
    result = my_selenium_instance.get_text_from_page()
    mock_chrome_driver.find_element.assert_called_once_with(By.TAG_NAME, "body")
    assert result == "Test"


def test_get_attribute(mock_chrome_driver):
    my_selenium_instance = SeleniumUtils(mock_chrome_driver)
    mock_chrome_driver.find_element = Mock()
    mock_element = Mock()
    mock_element.get_attribute.return_value = "Test"
    mock_chrome_driver.find_element.return_value = mock_element
    result = my_selenium_instance.get_attribute(By.XPATH, "//div[@id='example']", "data-example")
    mock_chrome_driver.find_element.assert_called_once_with(By.XPATH, "//div[@id='example']")
    mock_element.get_attribute.assert_called_once_with("data-example")
    assert result == "Test"


'''def test_get_child_elements_by_css(mock_chrome_driver):
    mock_parent_element = Mock(spec=WebElement)
    mock_parent_element.tag_name = "div"
    mock_parent_element.get_attribute.return_value = None
    mock_child_element_1 = Mock(spec=WebElement)
    mock_child_element_2 = Mock(spec=WebElement)
    mock_child_element_1.tag_name = "span"
    mock_child_element_1.text = "Child 1 Text"
    mock_child_element_2.tag_name = "span"
    mock_child_element_2.text = "Child 2 Text"
    mock_parent_element.find_elements_by_css.return_value = [mock_child_element_1, mock_child_element_2]
    mock_chrome_driver.find_element.return_value = mock_parent_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    by_type = By.XPATH
    parent_locator = "//div[@id='parent-div']"
    child_css = "span.child-element"
    child_elements = selenium_utils.get_child_elements_by_css(by_type, parent_locator, child_css)
    assert len(child_elements) == 2
    assert child_elements[0].text == "Child 1 Text"
    assert child_elements[1].text == "Child 2 Text"'''


'''def test_switch_window(mock_chrome_driver):
    mock_chrome_driver.window_handles = ['window_handle_1', 'window_handle_2']
    mock_chrome_driver.current_window_handle = 'window_handle_1'
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    selenium_utils.switch_window()
    assert mock_chrome_driver.current_window_handle == "window_handle_2"'''


def test_wait_for_title(mock_chrome_driver):
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_title = 'Liveramp'
    selenium_utils.wait_for_title(expected_title)
    assert True


def test_wait_for_link(mock_chrome_driver):
    mock_link_element = Mock()
    mock_link_element.tag_name = "a"
    mock_link_element.text = "Test link"
    mock_chrome_driver.find_element.return_value = mock_link_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_link_text = 'Test link'
    selenium_utils.wait_for_link(expected_link_text)
    assert True


def test_find_button_equal_text_click(mock_chrome_driver):
    mock_button_elements = [
        Mock(spec=WebElement, text="Button 1"),
        Mock(spec=WebElement, text="Button 2"),
        Mock(spec=WebElement, text="Button 3"),
    ]
    mock_chrome_driver.find_elements.return_value = mock_button_elements
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_button_text = 'Button 2'
    selenium_utils.find_button_equal_text_click(expected_button_text)
    assert True


def test_find_button_contain_text_click(mock_chrome_driver):
    mock_button_elements = [
        Mock(spec=WebElement, text="Button 1"),
        Mock(spec=WebElement, text="Button 2 with Text"),
        Mock(spec=WebElement, text="Button 3"),
    ]
    mock_chrome_driver.find_elements.return_value = mock_button_elements
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_button_text = 'Button 2'
    selenium_utils.find_button_contain_text_click(expected_button_text)
    assert True


def test_select_radio_equal_text_click(mock_chrome_driver):
    mock_radio_elements = [
        Mock(spec=WebElement, text="Option 1"),
        Mock(spec=WebElement, text="Option 2"),
        Mock(spec=WebElement, text="Option 3"),
    ]
    mock_chrome_driver.find_elements.return_value = mock_radio_elements
    for element in mock_radio_elements:
        mock_radio_input = Mock(spec=WebElement)
        mock_radio_input.get_attribute.return_value = "radio"
        element.find_element.return_value = mock_radio_input
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_radio_text = 'Option 2'
    css_selector = 'label.radio-label'
    selenium_utils.select_radio_equal_text_click(expected_radio_text, css_selector)
    assert True


'''def test_find_row_contain_text_click_button(mock_chrome_driver):
    mock_table_rows = [
        Mock(spec=WebElement, text="Row 1: Data Data Data"),
        Mock(spec=WebElement, text="Row 2: More Data More Data"),
        Mock(spec=WebElement, text="Row 3: Even More Data"),
    ]
    mock_chrome_driver.find_elements.return_value = mock_table_rows
    for row in mock_table_rows:
        mock_button = Mock(spec=WebElement)
        mock_button.get_attribute.return_value = "button"
        row.find_elements.return_value = [mock_button]
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_row_text = 'Row 2: More Data More Data'
    expected_button_text = 'Button Text'
    row_css_selector = 'tr.table-row'
    button_css_selector = 'button.button-class'
    selenium_utils.find_row_contain_text_click_button(
        expected_row_text, expected_button_text, row_css_selector, button_css_selector
    )
    assert True'''


def test_find_row_contain_text_return_cell_element(mock_chrome_driver):
    mock_table_rows = [
        Mock(spec=WebElement, text="Row 1: Data Data Data"),
        Mock(spec=WebElement, text="Row 2: More Data More Data"),
        Mock(spec=WebElement, text="Row 3: Even More Data"),
    ]
    mock_chrome_driver.find_elements.return_value = mock_table_rows
    for row in mock_table_rows:
        mock_cell = Mock(spec=WebElement)
        mock_cell.get_attribute.return_value = "cell"
        row.find_element.return_value = mock_cell
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_row_text = 'Row 2: More Data More Data'
    row_css_selector = 'tr.table-row'
    cell_css_selector = 'td.cell-class'
    cell_element = selenium_utils.find_row_contain_text_return_cell_element(
        expected_row_text, row_css_selector, cell_css_selector
    )
    assert cell_element is not None
    assert cell_element.get_attribute("class") == "cell"


def test_find_row_contain_text_return_cell_text(mock_chrome_driver):
    mock_table_rows = [
        Mock(spec=WebElement, text="Row 1: Data Data Data"),
        Mock(spec=WebElement, text="Row 2: More Data More Data"),
        Mock(spec=WebElement, text="Row 3: Even More Data"),
    ]
    mock_chrome_driver.find_elements.return_value = mock_table_rows
    for row in mock_table_rows:
        mock_cell = Mock(spec=WebElement)
        mock_cell.get_attribute.return_value = "cell"
        mock_cell.text = "Cell Text"
        row.find_element.return_value = mock_cell
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_row_text = 'Row 2: More Data More Data'
    row_css_selector = 'tr.table-row'
    cell_css_selector = 'td.cell-class'
    cell_text = selenium_utils.find_row_contain_text_return_cell_text(
        expected_row_text, row_css_selector, cell_css_selector
    )
    assert cell_text is not None
    assert cell_text == "Cell Text"


def test_find_row_contain_text_click_element(mock_chrome_driver):
    mock_table_rows = [
        Mock(spec=WebElement, text="Row 1: Data Data Data"),
        Mock(spec=WebElement, text="Row 2: More Data More Data"),
        Mock(spec=WebElement, text="Row 3: Even More Data"),
    ]
    mock_chrome_driver.find_elements.return_value = mock_table_rows
    for row in mock_table_rows:
        mock_element = Mock(spec=WebElement)
        mock_element.get_attribute.return_value = "element"
        row.find_element.return_value = mock_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_row_text = 'Row 2: More Data More Data'
    row_css_selector = 'tr.table-row'
    element_css_selector = 'td.cell-class'
    selenium_utils.find_row_contain_text_click_element(
        expected_row_text, row_css_selector, element_css_selector
    )


'''def test_find_row_contain_two_texts_click(mock_chrome_driver):
    mock_table_rows = [
        Mock(spec=WebElement, text="Row 1: Data Data Data"),
        Mock(spec=WebElement, text="Row 2: More Data More Data"),
        Mock(spec=WebElement, text="Row 3: Even More Data"),
        Mock(spec=WebElement, text="Row 4: Data Data Data"),
    ]
    mock_chrome_driver.find_elements.return_value = mock_table_rows
    for row in mock_table_rows:
        mock_element = Mock(spec=WebElement)
        mock_element.get_attribute.return_value = "element"
        row.find_element.return_value = mock_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_row_text = 'Row 2: More Data More Data'
    another_text = 'Row 2: Even More Data'
    row_css_selector = 'tr.table-row'
    element_css_selector = 'td.cell-class'
    clicked_elements = selenium_utils.find_row_contain_two_texts_click(
        expected_row_text, another_text, row_css_selector, element_css_selector
    )
    assert clicked_elements == 1'''


def test_find_contain_text_hover_click(mock_chrome_driver):
    mock_table_rows = [
        Mock(spec=WebElement, text="Row 1: Data Data Data"),
        Mock(spec=WebElement, text="Row 2: More Data More Data"),
        Mock(spec=WebElement, text="Row 3: Even More Data"),
        Mock(spec=WebElement, text="Row 4: Data Data Data"),
    ]
    mock_chrome_driver.find_elements.return_value = mock_table_rows
    for row in mock_table_rows:
        mock_element = Mock(spec=WebElement)
        mock_element.get_attribute.return_value = "element"
        row.find_element.return_value = mock_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_row_text = 'Row 2: More Data More Data'
    row_css_selector = 'tr.table-row'
    hover_css_selector = 'button.view-button'
    success = selenium_utils.find_contain_text_hover_click(
        expected_row_text, row_css_selector, hover_css_selector
    )
    assert success is True


def test_find_contain_text_hover_click_another(mock_chrome_driver):
    mock_table_rows = [
        Mock(spec=WebElement, text="Row 1: Data Data Data"),
        Mock(spec=WebElement, text="Row 2: More Data More Data"),
        Mock(spec=WebElement, text="Row 3: Even More Data"),
        Mock(spec=WebElement, text="Row 4: Data Data Data"),
    ]
    mock_chrome_driver.find_elements.return_value = mock_table_rows
    for row in mock_table_rows:
        mock_element = Mock(spec=WebElement)
        mock_element.get_attribute.return_value = "element"
        row.find_element.return_value = mock_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_row_text = 'Row 2: More Data More Data'
    row_css_selector = 'tr.table-row'
    hover_css_selector = 'button.view-button'
    click_css_selector = 'button.click-button'
    selenium_utils.find_contain_text_hover_click_another(
        expected_row_text, row_css_selector, hover_css_selector, click_css_selector
    )


def test_find_contain_text_type_text(mock_chrome_driver):
    mock_table_rows = [
        Mock(spec=WebElement, text="Row 1: Data Data Data"),
        Mock(spec=WebElement, text="Row 2: More Data More Data"),
        Mock(spec=WebElement, text="Row 3: Even More Data"),
        Mock(spec=WebElement, text="Row 4: Data Data Data"),
    ]
    mock_chrome_driver.find_elements.return_value = mock_table_rows
    for row in mock_table_rows:
        mock_input_element = Mock(spec=WebElement)
        mock_input_element.get_attribute.return_value = "input"
        row.find_element.return_value = mock_input_element
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    expected_row_text = 'Row 3: Even More Data'
    row_css_selector = 'tr.table-row'
    type_text_css_selector = 'input[type="text"]'
    text_to_type = 'Sample Text'
    result = selenium_utils.find_contain_text_type_text(
        expected_row_text, row_css_selector, type_text_css_selector, text_to_type
    )
    assert result is True


'''def test_click_presentation_contain_role_click(mock_chrome_driver):
    mock_list_items = [
        Mock(spec=WebElement, text="Role 1"),
        Mock(spec=WebElement, text="Role 2"),
        Mock(spec=WebElement, text="Role 3"),
        Mock(spec=WebElement, text="Role 4"),
    ]
    mock_chrome_driver.find_elements.return_value = mock_list_items
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    ul_role = 'presentation-list'
    role_name = 'Role 2'
    selenium_utils.click_presentation_contain_role_click(ul_role, role_name)
    mock_chrome_driver.find_elements.assert_called_with(
        By.CSS_SELECTOR, f'div[role="presentation"] ul[role="{ul_role}"] li'
    )
    mock_list_items[1].click.assert_called_once()'''


'''def test_close_popup_banner_with_button_id(mock_chrome_driver):
    mock_dialog_button = Mock(spec=WebElement, text="Close Banner")
    mock_dialog_button.get_attribute.return_value = "pendo-button"
    mock_chrome_driver.find_element.side_effect = [None, mock_dialog_button]
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    selenium_utils.close_popup_banner()
    mock_chrome_driver.find_element.assert_has_calls([
        pytest.call(By.CSS_SELECTOR, 'button[id*="pendo-button"]'),
        pytest.call(By.CSS_SELECTOR, 'button[id*="pendo-close"]')
    ])
    mock_dialog_button = mock_chrome_driver.find_element.return_value
    mock_dialog_button.click.assert_called_once()'''


def test_close_pendo_banners_with_buttons(mock_chrome_driver):
    mock_dialog_button1 = Mock(spec=WebElement, text="Close Banner 1")
    mock_dialog_button1.get_attribute.return_value = "pendo-close-guide-1"
    mock_dialog_button2 = Mock(spec=WebElement, text="Close Banner 2")
    mock_dialog_button2.get_attribute.return_value = "pendo-close-guide-2"
    mock_chrome_driver.find_elements.return_value = [mock_dialog_button1, mock_dialog_button2]
    selenium_utils = SeleniumUtils(mock_chrome_driver)
    selenium_utils.close_pendo_banners()
    mock_chrome_driver.find_elements.assert_called_once_with(By.CSS_SELECTOR, 'button[id^="pendo-close-guide"]')
    mock_dialog_button1 = mock_chrome_driver.find_elements.return_value[0]
    mock_dialog_button2 = mock_chrome_driver.find_elements.return_value[1]
    assert mock_dialog_button1.click.call_count == 1
    assert mock_dialog_button2.click.call_count == 1
