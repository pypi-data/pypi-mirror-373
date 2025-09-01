import pytest
from unittest.mock import Mock
from liveramp_automation.helpers.login import LoginHelper



@pytest.fixture
def mock_instance():
    mock_instance = Mock()
    mock_instance.current_url = 'https://liveramp.com/careers/'
    mock_instance.title = 'Liveramp'
    mock_instance.url = 'url'
    mock_instance.username = 'username'
    mock_instance.password = 'password'

    mock_element_1 = Mock()
    mock_element_1.get_attribute.return_value = "element_test_1"

    mock_element_2 = Mock()
    mock_element_2.get_attribute.return_value = "element_test_2"

    mock_element = Mock()
    mock_element.get_attribute.return_value = "element_test"

    mock_instance.find_elements.return_value = [mock_element_1, mock_element_2]
    mock_instance.find_element.return_value = mock_element

    return mock_instance


def test_okta_login_page(mock_instance):
    LoginHelper.liveramp_okta_login_page(mock_instance, mock_instance.url, mock_instance.username, mock_instance.password)
    # Add assertions to check the behavior of the method


def test_okta_login_driver(mock_instance):

    LoginHelper.liveramp_okta_login_driver(mock_instance, mock_instance.url, mock_instance.username, mock_instance.password)
    # Add assertions to check the behavior of the method


def test_call_oauth2_get_token(mock_instance):
    # Call the method with parameters
    LoginHelper.call_oauth2_get_token(mock_instance.username, mock_instance.password)
    # Add assertions to check the behavior of the method


def test_console_login_page(mock_instance):
    LoginHelper.liveramp_console_login_page(mock_instance, mock_instance.url, mock_instance.username, mock_instance.password)
