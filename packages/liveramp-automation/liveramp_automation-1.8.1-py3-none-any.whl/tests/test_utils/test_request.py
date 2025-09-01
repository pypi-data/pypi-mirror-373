from liveramp_automation.utils import request
from unittest.mock import patch
import requests
import pytest

def mocked_requests_response(*args, **kwargs):
    """Helper to create a mock successful requests.Response object."""
    response = requests.models.Response()
    response.status_code = 200
    return response

def mocked_requests_response_throw_HTTPError(*args, **kwargs):
    raise requests.exceptions.HTTPError("url", "", "HTTPError", None, None)

def mocked_requests_response_throw_RequestException(*args, **kwargs):
    raise requests.exceptions.RequestException("url", "", "RequestException", None, None)

def mocked_requests_response_throw_Timeout(*args, **kwargs):
    raise requests.exceptions.Timeout("url", "", "Timeout", None, None)

def mocked_requests_response_throw_ConnectionError(*args, **kwargs):
    raise requests.exceptions.ConnectionError("url", "", "ConnectionError", None, None)

def mocked_requests_response_binary(*args, **kwargs):
    """Helper to create a mock requests.Response object with binary content."""
    response = requests.models.Response()
    response.status_code = 200
    response.headers['Content-Type'] = 'image/jpeg'  # Simulate a binary content type
    response.raw = b'\xff\xd8\xff\xe0\x00\x10JFIF'  # Example JPEG header
    response._content = b'\xff\xd8\xff\xe0\x00\x10JFIF'
    return response

def mocked_requests_response_malformed_url(*args, **kwargs):
    response = requests.models.Response()
    response.status_code = 404
    response.reason = "Not Found"
    return response

def mocked_requests_response_empty_content(*args, **kwargs):
    response = requests.models.Response()
    response.status_code = 200
    response._content = b''  # Simulate empty content
    return response

def mocked_requests_response_binary_content(*args, **kwargs):
    response = requests.models.Response()
    response.status_code = 200
    response._content = b'\x89PNG\r\n\x1a\n...'  # Simulate binary content (PNG header)
    return response

def mocked_allure_method():
    pass

# Create fixtures for common test data
@pytest.fixture
def default_headers():
    return {"Content-Type": 'application/x-www-form-urlencoded'}

@pytest.fixture
def default_data():
    return {
        "test": "test"
    }

@pytest.fixture
def auth_data():
    return {
        "grant_type": "password",
        "scope": "openid",
        "client_id": "liveramp-api"
    }

@pytest.fixture
def default_url():
    return 'https://url/'

@pytest.fixture
def auth_url():
    return 'https://serviceaccounts.liveramp.com/authn/v1/oauth2/token'

# Parameterized tests for different HTTP methods with different exception types
@pytest.mark.parametrize("http_method, request_func", [
    ('post', request.request_post),
    ('get', request.request_get),
    ('delete', request.request_delete),
    ('options', request.request_options),
    ('head', request.request_head),
    ('put', request.request_put),
    ('patch', request.request_patch),
])
@pytest.mark.parametrize("exception_mock, exception_name", [
    (mocked_requests_response_throw_HTTPError, "HTTPError"),
    (mocked_requests_response_throw_RequestException, "RequestException"),
    (mocked_requests_response_throw_Timeout, "Timeout"),
])
@patch('allure.attach')
def test_request_methods_with_exceptions(mock_allure, http_method, request_func, 
                                         exception_mock, exception_name, 
                                         default_url, default_headers, default_data):
    """Test that all HTTP methods handle exceptions correctly."""
    with patch(f'requests.{http_method}', side_effect=exception_mock):
        response = request_func(default_url, headers=default_headers, data=default_data)
        assert response is None

# Parameterized tests for different HTTP methods with JSON data
@pytest.mark.parametrize("http_method, request_func", [
    ('post', request.request_post),
    ('get', request.request_get),
    ('delete', request.request_delete),
    ('head', request.request_head),
    ('put', request.request_put),
    ('patch', request.request_patch),
])
@patch('allure.attach')
def test_request_methods_with_json(mock_allure, http_method, request_func, 
                                  default_url, default_headers, default_data):
    """Test that all HTTP methods handle JSON data correctly."""
    with patch(f'requests.{http_method}', side_effect=mocked_requests_response):
        response = request_func(default_url, headers=default_headers, json=default_data)
        assert response is not None
        if http_method != 'get':  # get doesn't always return status_code in our mocks
            assert response.status_code == 200

# Keep individual tests for specific scenarios that don't fit the parameterized pattern
@patch('allure.attach')
def test_request_post_data(mock_allure, auth_url, default_headers, auth_data):
    response = request.request_post(auth_url, headers=default_headers, data=auth_data)
    assert response.status_code == 400

@patch('allure.attach')
def test_request_post_json(mock_allure, auth_url, default_headers, auth_data):
    response = request.request_post(auth_url, headers=default_headers, json=auth_data)
    assert response.status_code == 400

@patch('allure.attach')
@patch('requests.post', side_effect=mocked_requests_response)
def test_request_post_data_and_json(mock_post, mock_allure, auth_url, default_headers, auth_data):
    json_data = {"key": "value"}
    response = request.request_post(auth_url, headers=default_headers, data=auth_data, json=json_data)
    assert response.status_code == 200

@patch('allure.attach')
def test_request_post_invalid_url(mock_allure, default_headers):
    url = 'not-a-url'
    response = request.request_post(url, headers=default_headers)
    assert response is None

@patch('allure.attach')
@patch('requests.get')
def test_request_get(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_get(url, headers=headers, data=data)
    assert response is not None

@patch('allure.attach')
@patch('requests.get')
def test_request_get_json(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test" : "test"
    }
    response = request.request_get(url, headers=headers, data=None, json=data)
    assert response is not None

@patch('allure.attach')
@patch('requests.delete', side_effect=mocked_requests_response)
def test_request_delete(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_delete(url, headers=headers, data=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.delete', side_effect=mocked_requests_response)
def test_request_delete_json(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_delete(url, headers=headers, data=None, json=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.delete', side_effect=requests.exceptions.RequestException)
def test_request_delete_empty_url(mock1, mock2):
    url = None
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_delete(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.delete', side_effect=requests.exceptions.RequestException)
def test_request_delete_none_url(mock1, mock2):
    url = ""
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_delete(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.options', side_effect=mocked_requests_response_empty_content)
def test_request_options_empty_content(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    response = request.request_options(url, headers=headers)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.options', side_effect=mocked_requests_response_binary_content)
def test_request_options_binary_content(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    response = request.request_options(url, headers=headers)
    assert response.status_code == 200

@patch('allure.attach')
def test_request_options_invalid_url(mock):
    url = 'invalid-url'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    response = request.request_options(url, headers=headers)
    assert response is None

@patch('allure.attach')
@patch('requests.options', side_effect=mocked_requests_response)
def test_request_options(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_options(url, headers=headers, data=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.head', side_effect=mocked_requests_response)
def test_request_head(mock1, mock2):
    url = 'https://www.google.com/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_head(url, headers=headers, data=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.head', side_effect=mocked_requests_response)
def test_request_head_json(mock1, mock2):
    url = 'https://www.google.com/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_head(url, headers=headers, data=None, json=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.put', side_effect=mocked_requests_response)
def test_request_put(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_put(url, headers=headers, data=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.put', side_effect=mocked_requests_response)
def test_request_put_json(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_put(url, headers=headers, data=None, json=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.patch', side_effect=mocked_requests_response)
def test_request_patch(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_patch(url, headers=headers, data=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.patch', side_effect=mocked_requests_response)
def test_request_patch_json(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    response = request.request_patch(url, headers=headers, data=None, json=data)
    assert response.status_code == 200

@patch('allure.attach')
@patch('requests.post', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_post_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_post(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_get_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    response = request.request_get(url, headers=headers)
    assert response is None

@patch('allure.attach')
@patch('requests.delete', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_delete_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_delete(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.options', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_options_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_options(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.head', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_head_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_head(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.put', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_put_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_put(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.patch', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_patch_HTTPError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_patch(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.post', side_effect=mocked_requests_response_throw_RequestException)
def test_request_post_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_post(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response_throw_RequestException)
def test_request_get_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    response = request.request_get(url, headers=headers)
    assert response is None

@patch('allure.attach')
@patch('requests.delete', side_effect=mocked_requests_response_throw_RequestException)
def test_request_delete_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_delete(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.options', side_effect=mocked_requests_response_throw_RequestException)
def test_request_options_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_options(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.head', side_effect=mocked_requests_response_throw_RequestException)
def test_request_head_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_head(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.put', side_effect=mocked_requests_response_throw_RequestException)
def test_request_put_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_put(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.patch', side_effect=mocked_requests_response_throw_RequestException)
def test_request_patch_RequestException(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_patch(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.post', side_effect=mocked_requests_response_throw_Timeout)
def test_request_post_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_post(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response_throw_Timeout)
def test_request_get_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    response = request.request_get(url, headers=headers)
    assert response is None

@patch('allure.attach')
@patch('requests.delete', side_effect=mocked_requests_response_throw_Timeout)
def test_request_delete_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_delete(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.options', side_effect=mocked_requests_response_throw_Timeout)
def test_request_options_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_options(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.head', side_effect=mocked_requests_response_throw_Timeout)
def test_request_head_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_head(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.put', side_effect=mocked_requests_response_throw_Timeout)
def test_request_put_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_put(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.patch', side_effect=mocked_requests_response_throw_Timeout)
def test_request_patch_Timeout(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_patch(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.request', side_effect=mocked_requests_response)
def test_request_any_post_with_json(mock_requests_request, mock_allure_attach):
    """
    Tests that request_any successfully sends a POST request with json
    and returns a valid response object.
    """
    # Arrange
    method = 'POST'
    url = 'https://api.example.com/resource'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer test_token'}
    json_data = {'key1': 'value1', 'key2': 'value2'}

    # Act
    response = request.request_any(method, url, headers=headers, json=json_data)

    # Assert
    assert response is not None
    assert response.status_code == 200
    mock_requests_request.assert_called_once_with(
        method,
        url=url,
        data=None,
        json=json_data,
        headers=headers
    )

@patch('allure.attach')
@patch('requests.request', side_effect=mocked_requests_response)
def test_request_any_put_with_kwargs(mock_requests_request, mock_allure_attach):
    """
    Tests that request_any successfully sends a PUT request with headers and kwargs
    and returns a valid response object.
    """
    # Arrange
    method = 'PUT'
    url = 'https://api.example.com/resource'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer test_token'}
    timeout = 10

    # Act
    response = request.request_any(method, url, headers=headers, timeout=timeout)

    # Assert
    assert response is not None
    assert response.status_code == 200
    mock_requests_request.assert_called_once_with(
        method,
        url=url,
        data=None,
        json=None,
        headers=headers,
        timeout=timeout
    )

@patch('allure.attach')
@patch('requests.request', side_effect=mocked_requests_response)
def test_request_any_get_with_data(mock_requests_request, mock_allure_attach):
    """
    Tests that request_any successfully sends a GET request with data
    and returns a valid response object.
    """
    # Arrange
    method = 'GET'
    url = 'https://api.example.com/resource'
    headers = {'Content-Type': 'application/json', 'Authorization': 'Bearer test_token'}
    data = {'key1': 'value1', 'key2': 'value2'}

    # Act
    response = request.request_any(method, url, headers=headers, data=data)

    # Assert
    assert response is not None
    assert response.status_code == 200
    mock_requests_request.assert_called_once_with(
        method,
        url=url,
        data=data,
        json=None,
        headers=headers
    )

@patch('allure.attach')
@patch('requests.request', side_effect=requests.exceptions.RequestException("Connection error"))
def test_request_any_network_error(mock_requests_request, mock_allure_attach):
    """
    Tests that request_any returns None when a network error (RequestException) occurs.
    """
    # Arrange
    method = 'GET'
    url = 'https://api.example.com/resource'
    headers = {'Content-Type': 'application/json'}

    # Act
    response = request.request_any(method, url, headers=headers)

    # Assert
    assert response is None

@patch('allure.attach')
@patch('requests.request', side_effect=mocked_requests_response_throw_HTTPError)
def test_request_any_HTTPError(mock_requests_request, mock_allure_attach):
    """
    Tests that request_any handles HTTPError exceptions correctly.
    """
    # Arrange
    method = 'GET'
    url = 'https://api.example.com/resource'
    headers = {'Content-Type': 'application/json'}

    # Act
    response = request.request_any(method, url, headers=headers)

    # Assert
    assert response is None

@patch('allure.attach')
@patch('requests.request', side_effect=mocked_requests_response_throw_Timeout)
def test_request_any_timeout(mock_requests_request, mock_allure_attach):
    """
    Tests that request_any handles Timeout exceptions correctly.
    """
    # Arrange
    method = 'GET'
    url = 'https://api.example.com/resource'
    headers = {'Content-Type': 'application/json'}

    # Act
    response = request.request_any(method, url, headers=headers)

    # Assert
    assert response is None
    mock_requests_request.assert_called_once_with(
        method,
        url=url,
        data=None,
        json=None,
        headers=headers
    )

@patch('allure.attach')
@patch('requests.request', side_effect=mocked_requests_response)
def test_request_any_lowercase_method(mock_requests_request, mock_allure_attach):
    """
    Tests that request_any correctly handles lowercase HTTP method names.
    """
    # Arrange
    method = 'get'  # Lowercase method name
    url = 'https://api.example.com/resource'
    headers = {'Content-Type': 'application/json'}

    # Act
    response = request.request_any(method, url, headers=headers)

    # Assert
    assert response is not None
    assert response.status_code == 200
    mock_requests_request.assert_called_once_with(
        method,  # Verify that the lowercase method is passed to requests.request
        url=url,
        data=None,
        json=None,
        headers=headers
    )

@patch('allure.attach')
@patch('requests.request', side_effect=mocked_requests_response_binary)
def test_request_any_binary_response(mock_requests_request, mock_allure_attach):
    """
    Tests that request_any handles binary responses without errors.
    """
    # Arrange
    method = 'GET'
    url = 'https://example.com/image.jpg'
    headers = {}

    # Act
    response = request.request_any(method, url, headers=headers)

    # Assert
    assert response is not None
    assert response.status_code == 200
    mock_requests_request.assert_called_once_with(method, url=url, data=None, json=None, headers=headers)

@patch('requests.request')
@patch('allure.attach')
def test_request_any_invalid_method(mock_allure_attach, mock_request):
    """
    Tests that request_any raises a ValueError when called with an invalid HTTP method.
    """
    # Arrange
    mock_request.side_effect = ValueError("Invalid HTTP Method")
    method = 'INVALID'
    url = 'https://api.example.com/resource'
    headers = {'Content-Type': 'application/json'}

    # Act & Assert
    with pytest.raises(ValueError):
        request.request_any(method, url, headers=headers)

@patch('allure.attach')
@patch('requests.request', side_effect=mocked_requests_response)
def test_request_any_with_data_and_json(mock_requests_request, mock_allure_attach):
    """
    Tests that request_any successfully sends a request with both data and json parameters.
    """
    # Arrange
    method = 'POST'
    url = 'https://api.example.com/resource'
    headers = {'Content-Type': 'application/json'}
    data = {'key1': 'value1', 'key2': 'value2'}
    json_data = {'key3': 'value3', 'key4': 'value4'}

    # Act
    response = request.request_any(method, url, headers=headers, data=data, json=json_data)

    # Assert
    assert response is not None
    assert response.status_code == 200
    mock_requests_request.assert_called_once_with(
        method,
        url=url,
        data=data,
        json=json_data,
        headers=headers
    )

@patch('allure.attach')
@patch('requests.request')
def test_request_any_malformed_url(mock_requests_request, mock_allure_attach):
    """
    Tests that request_any handles malformed URLs correctly by returning None.
    """
    # Arrange
    method = 'GET'
    url = '://malformed_url'  # Malformed URL
    headers = {'Content-Type': 'application/json'}
    mock_requests_request.side_effect = requests.exceptions.RequestException("Malformed URL")

    # Act
    response = request.request_any(method, url, headers=headers)

    # Assert
    assert response is None

@patch('allure.attach')
@patch('requests.post', side_effect=mocked_requests_response_malformed_url)
def test_request_post_malformed_url(mock1, mock2):
    url = 'https://invaliddomain'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "grant_type": "password",
        "scope": "openid",
        "client_id": "liveramp-api"
    }
    response = request.request_post(url, headers=headers, data=data)
    assert response.status_code == 404

@patch('allure.attach')
@patch('requests.post', side_effect=mocked_requests_response_throw_ConnectionError)
def test_request_post_ConnectionError(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {}
    response = request.request_post(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.post', side_effect=mocked_requests_response_throw_RequestException)
def test_request_post_headers_none(mock1, mock2):
    url = 'https://url/'
    data = {}
    response = request.request_post(url, headers=None, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.post', side_effect=mocked_requests_response_throw_RequestException)
def test_request_post_headers_not_dict(mock1, mock2):
    url = 'https://url/'
    headers = 123
    data = {}
    response = request.request_post(url, headers=headers, data=data)
    assert response is None

@patch('allure.attach')
@patch('requests.get')
def test_request_get_headers_none(mock_get, mock_attach):
    url = 'https://url/'
    mock_get.side_effect = requests.exceptions.RequestException("Invalid headers")
    response = request.request_get(url, headers=None)
    assert response is None

@patch('allure.attach')
@patch('requests.get')
def test_request_get_headers_not_dict(mock_get, mock_attach):
    url = 'https://url/'
    mock_get.side_effect = requests.exceptions.RequestException("Invalid headers")
    response = request.request_get(url, headers="not a dict")
    assert response is None

@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response)
def test_request_get_data_and_json(mock1, mock2):
    url = 'https://url/'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    data = {
        "test": "test"
    }
    json_data = {
        "test_json": "test_json"
    }
    response = request.request_get(url, headers=headers, data=data, json=json_data)
    assert response is not None

@patch('allure.attach')
@patch('requests.get')
def test_request_get_malformed_url(mock_get, mock_allure_attach):
    mock_get.side_effect = requests.exceptions.RequestException("Malformed URL")
    url = 'malformed_url'
    headers = {"Content-Type": 'application/x-www-form-urlencoded'}
    response = request.request_get(url, headers=headers)
    assert response is None

# Parameterized tests for request_any with different HTTP methods
@pytest.mark.parametrize("method", ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS', 'HEAD'])
@patch('allure.attach')
@patch('requests.request', side_effect=mocked_requests_response)
def test_request_any_with_different_methods(mock_request, mock_allure, method):
    """Tests that request_any works with different HTTP methods."""
    url = 'https://api.example.com/resource'
    headers = {'Content-Type': 'application/json'}
    
    response = request.request_any(method, url, headers=headers)
    
    assert response is not None
    assert response.status_code == 200
    mock_request.assert_called_once_with(
        method,
        url=url,
        data=None,
        json=None,
        headers=headers
    )

# Parameterized tests for invalid headers
@pytest.mark.parametrize("http_method, request_func", [
    ('post', request.request_post),
    ('get', request.request_get),
])
@pytest.mark.parametrize("headers, header_desc", [
    (None, "none"),
    (123, "not_dict"),
])
@patch('allure.attach')
def test_request_methods_invalid_headers(mock_allure, http_method, request_func, 
                                        headers, header_desc, default_url, default_data):
    """Test that HTTP methods handle invalid headers correctly."""
    with patch(f'requests.{http_method}', side_effect=requests.exceptions.RequestException):
        response = request_func(default_url, headers=headers, data=default_data)
        assert response is None