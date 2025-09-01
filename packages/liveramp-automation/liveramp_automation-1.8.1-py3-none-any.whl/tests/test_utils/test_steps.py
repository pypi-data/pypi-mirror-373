import pytest
from unittest.mock import Mock, patch
from json import JSONDecodeError
import requests
from datetime import date
from liveramp_automation.utils.steps import verify_endpoint_response_exist, verify_request_config_response_exist_fields, verify_request_config_response_exist_substring, replace_macros, get_dict_data, generate_url_from_dict, set_request_url_parameter_list, set_env_domain_path, headers, set_request_body_yaml


# Helper function to assert that a function doesn't raise an exception
def assert_no_exception(func, *args, **kwargs):
    """
    Helper function to assert that a function doesn't raise an exception.
    If an exception is raised, the test fails with a clear message.
    """
    try:
        return func(*args, **kwargs)
    except Exception as e:
        pytest.fail(f"Function {func.__name__} raised an unexpected exception: {e}")


class TestVerifyEndpointResponseExist:
    """
    Test suite for the verify_endpoint_response_exist step function.
    """

    def setup_mock_response(self, response_json=None, side_effect=None):
        """
        Helper method to set up a mock response object.
        """
        mock_response_body = Mock()
        if response_json is not None:
            mock_response_body.json.return_value = response_json
        if side_effect is not None:
            mock_response_body.json.side_effect = side_effect
        return mock_response_body

    def test_happy_path_with_string_list_of_fields(self):
        """
        Tests that verify_endpoint_response_exist correctly evaluates a string
        representation of a list for the 'fields' parameter and finds all
        fields in the response JSON keys.
        """
        # Arrange
        fields_to_check = "['user_id', 'name']"
        response_json = {
            'user_id': 123,
            'name': 'John Doe',
            'email': 'john.doe@example.com'
        }
        mock_response_body = self.setup_mock_response(response_json=response_json)

        # Act & Assert
        assert_no_exception(verify_endpoint_response_exist, fields_to_check, mock_response_body)

    def test_json_decode_error(self):
        """
        Tests that verify_endpoint_response_exist raises a JSONDecodeError when
        the response body does not contain valid JSON.
        """
        # Arrange
        fields = "['some_field']"
        mock_response_body = self.setup_mock_response(
            side_effect=JSONDecodeError("Expecting value", "<document>", 0)
        )

        # Act & Assert
        with pytest.raises(JSONDecodeError):
            verify_endpoint_response_exist(fields, mock_response_body)

    def test_raises_attribute_error_when_response_is_json_array(self):
        """
        Tests that verify_endpoint_response_exist raises an AttributeError
        when the response body is a JSON array, as .keys() is not a valid
        method for arrays.
        """
        # Arrange
        fields_to_check = "['user_id', 'name']"
        mock_response_body = self.setup_mock_response(response_json=[1, 2, 3])  # JSON array

        # Act & Assert
        with pytest.raises(AttributeError):
            verify_endpoint_response_exist(fields_to_check, mock_response_body)


class TestVerifyRequestConfigResponseExistFields:
    """
    Test suite for the verify_request_config_response_exist_fields step function.
    """

    def setup_mock_response(self, response_json=None, side_effect=None):
        """
        Helper method to set up a mock response object.
        """
        mock_response = Mock()
        if response_json is not None:
            mock_response.json.return_value = response_json
        if side_effect is not None:
            mock_response.json.side_effect = side_effect
        return mock_response

    def test_field_exists_in_response_body(self):
        """
        Tests that verify_request_config_response_exist_fields passes when the
        specified field exists as a key in the JSON response body.
        """
        # Arrange
        field_to_check = 'user_id'
        response_json = {
            'user_id': 42,
            'username': 'testuser',
            'status': 'active'
        }
        mock_response = self.setup_mock_response(response_json=response_json)
        request_config = {
            'response_body': mock_response
        }

        # Act & Assert
        assert_no_exception(verify_request_config_response_exist_fields, field_to_check, request_config)

    def test_handles_non_json_response_body(self):
        """
        Tests that verify_request_config_response_exist_fields handles non-JSON
        response bodies gracefully by raising a json.JSONDecodeError.
        """
        # Arrange
        field_to_check = 'some_field'
        mock_response = self.setup_mock_response(
            side_effect=JSONDecodeError("Expecting value", "test", 0)
        )
        mock_response.text = 'This is not JSON'
        request_config = {
            'response_body': mock_response
        }

        # Act & Assert
        with pytest.raises(JSONDecodeError):
            verify_request_config_response_exist_fields(field_to_check, request_config)

    def test_missing_response_body_key(self):
        """
        Tests that verify_request_config_response_exist_fields raises a KeyError
        when the 'response_body' key is missing from the request_config dictionary.
        """
        # Arrange
        field_to_check = 'user_id'
        request_config = {}  # Missing 'response_body' key

        # Act & Assert
        with pytest.raises(KeyError) as excinfo:
            verify_request_config_response_exist_fields(field_to_check, request_config)

        # Optionally, verify the error message.  This might make the test more brittle.
        assert "'response_body'" in str(excinfo.value)


class TestVerifyRequestConfigResponseExistSubstring:
    """
    Test suite for the verify_request_config_response_exist_substring step function.
    """

    def setup_mock_response(self, content=None, status_code=200):
        """
        Helper method to set up a mock response object.
        """
        mock_response = requests.models.Response()
        mock_response.status_code = status_code
        if content is not None:
            mock_response._content = content
        return mock_response

    def test_substring_exists_in_response_text(self):
        """
        Tests that the function passes when the substring exists in the response body's text.
        """
        # Arrange
        substring_to_find = "action successful"
        mock_response = self.setup_mock_response(
            content=b'{"message": "action successful", "status": 200}'
        )
        request_config = {
            "response_body": mock_response
        }

        # Act & Assert
        assert_no_exception(verify_request_config_response_exist_substring, substring_to_find, request_config)

    def test_response_body_is_none(self):
        """
        Tests that the function raises an AttributeError when response_body is None.
        """
        # Arrange
        substring_to_find = "any_substring"
        request_config = {
            "response_body": None
        }

        # Act & Assert
        with pytest.raises(AttributeError):
            verify_request_config_response_exist_substring(substring_to_find, request_config)

    def test_handles_binary_response_data(self):
        """
        Tests that the function handles binary response data appropriately.
        """
        # Arrange
        substring_to_find = "JFIF"  # A common substring in JPEG images
        binary_data = b"\xFF\xD8\xFF\xE0\x00\x10JFIF"  # Minimal JPEG header
        mock_response = self.setup_mock_response(content=binary_data)
        request_config = {
            "response_body": mock_response
        }

        # Act & Assert
        assert_no_exception(verify_request_config_response_exist_substring, substring_to_find, request_config)


class TestReplaceMacros:
    """
    Test suite for the replace_macros utility function.
    """

    def test_happy_path_string_with_valid_placeholders(self):
        """
        Tests that replace_macros correctly replaces all placeholders in a string
        with their corresponding values from the macros dictionary.
        """
        # Arrange
        input_string = "The user is {user_name} with ID {user_id}."
        macros = {
            'user_name': 'Alice',
            'user_id': 123
        }
        expected_string = "The user is Alice with ID 123."

        # Act
        result = replace_macros(input_string, macros)

        # Assert
        assert result == expected_string

    def test_returns_original_value_for_non_string_list_or_dict(self):
        """
        Tests that replace_macros returns the original value when the input is not a string, list, or dictionary.
        """
        # Arrange
        input_int = 123
        input_none = None
        macros = {'key': 'value'}

        # Act
        result_int = replace_macros(input_int, macros)
        result_none = replace_macros(input_none, macros)

        # Assert
        assert result_int == input_int
        assert result_none == input_none
        
    def test_string_with_missing_placeholder_raises_keyerror(self):
        """
        Tests that replace_macros raises a KeyError when a placeholder in the string
        is not found in the macros dictionary.
        """
        # Arrange
        input_string = "The user is {user_name} with ID {user_id} and email {user_email}."
        macros = {
            'user_name': 'Alice',
            'user_id': 123
        }

        # Act & Assert
        with pytest.raises(KeyError):
            replace_macros(input_string, macros)
            
    def test_complex_nested_data_structure(self):
        """
        Tests that replace_macros correctly processes complex nested data structures
        with mixed types (dict, list, string, int).
        """
        # Arrange
        data = {
            "level1": [
                {
                    "level2": "Value is {value1}",
                    "level2_int": 123
                },
                {
                    "level2": "Another value {value2}",
                    "level2_list": [
                        "item1",
                        "item2 {value3}"
                    ]
                }
            ],
            "level1_str": "Top level string {value1}"
        }
        macros = {
            "value1": "test1",
            "value2": "test2",
            "value3": "test3"
        }
        expected_data = {
            "level1": [
                {
                    "level2": "Value is test1",
                    "level2_int": 123
                },
                {
                    "level2": "Another value test2",
                    "level2_list": [
                        "item1",
                        "item2 test3"
                    ]
                }
            ],
            "level1_str": "Top level string test1"
        }

        # Act
        result = replace_macros(data, macros)

        # Assert
        assert result == expected_data
        
    def test_string_with_unmatched_braces_raises_value_error(self):
        """
        Tests that replace_macros raises a ValueError when the input string
        contains unmatched braces.
        """
        # Arrange
        input_string = "The value is {unclosed"
        macros = {}

        # Act & Assert
        with pytest.raises(ValueError):
            replace_macros(input_string, macros)

    def test_string_with_unmatched_braces_closed_raises_value_error(self):
        """
        Tests that replace_macros raises a ValueError when the input string
        contains unmatched closing braces.
        """
        # Arrange
        input_string = "The value is closed}"
        macros = {}

        # Act & Assert
        with pytest.raises(ValueError):
            replace_macros(input_string, macros)
            
    def test_circular_reference_raises_recursion_error(self):
        """
        Tests that replace_macros raises a RecursionError when a circular
        reference is present in the data structure.
        """
        # Arrange
        data = {}
        data['self'] = data  # Create a circular reference
        macros = {}

        # Act & Assert
        with pytest.raises(RecursionError):
            replace_macros(data, macros)


class TestGetDictData:
    """
    Test suite for the get_dict_data utility function.
    """

    @patch('liveramp_automation.utils.steps.MACROS', new={
        'test_today': '2023-10-27',
        'test_user': 'test_user_123'
    })
    def test_returns_value_with_macros_replaced(self):
        """
        Tests that get_dict_data correctly retrieves a value by its key
        and replaces all macro placeholders within it.
        """
        # Arrange
        body_key = 'request_params'
        res = {
            'other_key': 'some_value',
            'request_params': {
                'date': '{test_today}',
                'user': '{test_user}',
                'static_value': 'no_macro_here',
                'details': [
                    'Request for user {test_user} on {test_today}',
                    {'id': 42}
                ]
            }
        }
        expected_output = {
            'date': '2023-10-27',
            'user': 'test_user_123',
            'static_value': 'no_macro_here',
            'details': [
                'Request for user test_user_123 on 2023-10-27',
                {'id': 42}
            ]
        }

        # Act
        actual_output = get_dict_data(res, body_key)

        # Assert
        assert actual_output == expected_output

    def test_raises_key_error_when_key_not_found(self):
        """
        Tests that get_dict_data raises a KeyError when the specified
        body_key is not found in the res dictionary.
        """
        # Arrange
        res = {'other_key': 'some_value'}
        body_key = 'missing_key'

        # Act & Assert
        with pytest.raises(KeyError) as exc_info:
            get_dict_data(res, body_key)

        # Assert that the correct error message is raised
        assert f"'{body_key}'" in str(exc_info.value)

    def test_handles_non_string_list_dict_values(self):
        """
        Tests that get_dict_data correctly handles non-string, non-list, non-dictionary
        values (like integers, booleans, or None) retrieved from res[body_key].
        """
        # Arrange
        body_key = 'request_params'
        res = {
            'other_key': 'some_value',
            'request_params': 123
        }
        expected_output = 123

        # Act
        actual_output = get_dict_data(res, body_key)

        # Assert
        assert actual_output == expected_output


class TestGenerateUrlFromDict:
    """
    Test suite for the generate_url_from_dict utility function.
    """

    @pytest.mark.parametrize("base_url, params, expected_url", [
        # Test case 1: Multiple parameters
        (
            "https://api.liveramp.com/v1/users",
            {
                "name": "John Doe",
                "page": 1,
                "active": "true"
            },
            "https://api.liveramp.com/v1/users?name=John Doe&page=1&active=true"
        ),
        # Test case 2: Data type conversion
        (
            "https://api.example.com/data",
            {
                "int_value": 123,
                "float_value": 45.67,
                "bool_value": True
            },
            "https://api.example.com/data?int_value=123&float_value=45.67&bool_value=True"
        ),
        # Test case 3: URL encoding of special characters
        (
            "https://example.com/search",
            {
                "query": "test string with spaces & and =?#",
            },
            "https://example.com/search?query=test string with spaces & and =?#"
        ),
        # Test case 4: Empty base URL
        (
            "",
            {
                "name": "John Doe",
                "page": 1,
                "active": "true"
            },
            "?name=John Doe&page=1&active=true"
        ),
        # Test case 5: None base URL
        (
            None,
            {
                "name": "John Doe",
                "page": 1,
                "active": "true"
            },
            "None?name=John Doe&page=1&active=true"
        ),
        # Test case 6: List and nested dict values
        (
            "https://api.example.com/data",
            {
                "list_data": [1, 2, 3],
                "nested_dict": {"a": "b", "c": "d"}
            },
            "https://api.example.com/data?list_data=[1, 2, 3]&nested_dict={'a': 'b', 'c': 'd'}"
        ),
    ])
    def test_generate_url_from_dict(self, base_url, params, expected_url):
        """
        Tests various scenarios for generate_url_from_dict function.
        """
        # Act
        actual_url = generate_url_from_dict(params, base_url)

        # Assert
        assert actual_url == expected_url


class TestSetRequestUrlParameterList:
    """
    Test suite for the set_request_url_parameter_list function.
    """

    def test_happy_path_update_api_url(self):
        """
        Tests that set_request_url_parameter_list updates request_config['api_url']
        with parameters from url_params when both are valid.
        """
        # Arrange
        config = {}
        request_config = {"api_url": "https://api.example.com/v1/users"}
        url_params = {"user_id": "123", "account_id": "456"}

        # Mock get_dict_data to return the url_params directly
        with patch("liveramp_automation.utils.steps.get_dict_data", return_value=url_params):
            # Act
            updated_config = set_request_url_parameter_list(config, request_config, "url_params")

        # Assert
        expected_url = "https://api.example.com/v1/users?user_id=123&account_id=456"
        assert updated_config["api_url"] == expected_url

    def test_happy_path_updates_url_with_parameters(self):
        """
        Tests that set_request_url_parameter_list correctly updates the
        request_config['api_url'] with parameters from the config dictionary.
        """
        # Arrange
        config = {
            "api_params": {
                "id": "123",
                "user": "test"
            }
        }
        request_config = {
            "api_url": "http://api.test.com/v1/users"
        }
        url_params_key = "api_params"

        # Act
        updated_request_config = set_request_url_parameter_list(
            config, request_config, url_params_key
        )

        # Assert
        expected_url = "http://api.test.com/v1/users?id=123&user=test"
        assert updated_request_config["api_url"] == expected_url
        # Verify the original dictionary was mutated as expected
        assert request_config["api_url"] == expected_url

    def test_raises_key_error_when_url_params_key_missing(self):
        """
        Tests that set_request_url_parameter_list raises a KeyError when the
        url_params key does not exist in the config dictionary.
        """
        # Arrange
        config = {}
        request_config = {
            "api_url": "http://api.test.com/v1/users"
        }
        url_params_key = "api_params"

        # Act & Assert
        with pytest.raises(KeyError):
            set_request_url_parameter_list(config, request_config, url_params_key)


class TestSetEnvDomainPath:
    """
    Test suite for the set_env_domain_path step function.
    """

    def test_happy_path_with_formatted_domain(self):
        """
        Tests that set_env_domain_path correctly sets the request_url
        by formatting the domain string, looking it up in the res dictionary,
        and concatenating it with the provided path.
        """
        # Arrange
        res = {
            'env': 'qa',
            'qa_api_domain': 'https://qa.api.example.com'
        }
        request_config = {}
        domain = '{env}_api_domain'
        path = '/v1/users'
        expected_url = 'https://qa.api.example.com/v1/users'

        # Act
        updated_request_config = set_env_domain_path(res, request_config, domain, path)

        # Assert
        assert 'request_url' in updated_request_config
        assert updated_request_config['request_url'] == expected_url
        # Also assert that the original dictionary object was modified and returned
        assert updated_request_config is request_config

    def test_key_error_raised_when_domain_name_not_in_res(self):
        """
        Tests that a KeyError is raised when the formatted domain_name
        doesn't exist as a key in the res dictionary.
        """
        # Arrange
        res = {
            'env': 'qa',
        }
        request_config = {}
        domain = '{env}_api_domain'
        path = '/v1/users'

        # Act & Assert
        with pytest.raises(KeyError):
            set_env_domain_path(res, request_config, domain, path)

    def test_non_string_domain_value_raises_type_error(self):
        """
        Tests that a TypeError is raised when the domain value in 'res' is not a string.
        """
        # Arrange
        res = {
            'env': 'qa',
            'qa_api_domain': None  # Non-string value
        }
        request_config = {}
        domain = '{env}_api_domain'
        path = '/v1/users'

        # Act & Assert
        with pytest.raises(TypeError):
            set_env_domain_path(res, request_config, domain, path)

    def test_domain_format_key_error(self):
        """
        Tests that a KeyError is raised when the domain string contains format
        placeholders that don't exist in the res dictionary.
        """
        # Arrange
        res = {
            'env': 'qa',
        }
        request_config = {}
        domain = '{env}_api_domain_{non_existent_key}'
        path = '/v1/users'

        # Act & Assert
        with pytest.raises(KeyError):
            set_env_domain_path(res, request_config, domain, path)


class TestHeaders:
    """
    Test suite for the headers step function.
    """

    def test_happy_path_parses_multiline_string(self):
        """
        Tests that the headers function correctly parses a valid multi-line
        header string and populates the request_config dictionary.
        """
        # Arrange
        config = {'some_key': 'some_value'}
        token = 'dummy-token-123'
        request_config = {}
        headers_str = """
        Content-Type: application/json
        Accept: */*
        X-Custom-Header: MyValue
        """

        expected_headers = {
            'Content-Type': 'application/json',
            'Accept': '*/*',
            'X-Custom-Header': 'MyValue'
        }

        # Act
        updated_request_config = headers(config, headers_str, token, request_config)

        # Assert
        assert "headers" in updated_request_config
        assert updated_request_config["headers"] == expected_headers
        assert updated_request_config is request_config  # Ensure the original dict is modified in-place

    def test_strips_whitespace_around_keys_and_values(self):
        """
        Tests that the headers function strips whitespace around header keys and values.
        """
        # Arrange
        config = {}
        token = ''
        request_config = {}
        headers_str = """
          Key1  :   Value1  
          Key2   : Value2   
        """

        expected_headers = {
            'Key1': 'Value1',
            'Key2': 'Value2'
        }

        # Act
        updated_request_config = headers(config, headers_str, token, request_config)

        # Assert
        assert "headers" in updated_request_config
        assert updated_request_config["headers"] == expected_headers
        
    def test_key_error_raised_on_missing_config_key(self):
        """
        Tests that a KeyError is raised when the headers_str contains a
        placeholder for a key that doesn't exist in the config dictionary.
        """
        # Arrange
        config = {'some_key': 'some_value'}
        token = 'dummy-token-123'
        request_config = {}
        headers_str = """
        Content-Type: application/json
        X-Missing-Header: {missing_key}
        """

        # Act & Assert
        with pytest.raises(KeyError):
            headers(config, headers_str, token, request_config)
            
    def test_handles_header_values_with_colons(self):
        """
        Tests that the headers function correctly handles header values that contain colons.
        """
        # Arrange
        config = {}
        token = 'dummy-token-123'
        request_config = {}
        headers_str = """
        Authorization: Bearer abc:def
        """

        expected_headers = {
            'Authorization': 'Bearer abc:def'
        }

        # Act
        updated_request_config = headers(config, headers_str, token, request_config)

        # Assert
        assert "headers" in updated_request_config
        assert updated_request_config["headers"] == expected_headers

    def test_token_is_none_with_token_placeholder(self):
        """
        Tests that the headers function handles the case when token is None
        but headers_str contains '{token}' placeholder.
        """
        # Arrange
        config = {}
        token = None
        request_config = {}
        headers_str = """
        Authorization: Bearer {token}
        Content-Type: application/json
        """

        expected_headers = {
            'Authorization': 'Bearer None',
            'Content-Type': 'application/json'
        }

        # Act
        updated_request_config = headers(config, headers_str, token, request_config)

        # Assert
        assert "headers" in updated_request_config
        assert updated_request_config["headers"] == expected_headers


class TestSetRequestBodyYaml:
    """
    Test suite for the set_request_body_yaml step function.
    """

    def test_happy_path_sets_body_correctly(self):
        """
        Tests that set_request_body_yaml correctly sets the 'body' key in
        request_config when body_name exists in config and get_dict_data
        returns a valid dictionary, including processing macros.
        """
        # Arrange
        body_name = "sample_body"
        config = {
            "sample_body": {
                "id": 123,
                "user": "test_user",
                "date": "{today}"
            }
        }
        # Initialize request_config with a pre-existing key to ensure it's preserved.
        request_config = {"existing_key": "existing_value"}

        # Calculate the expected body after macro replacement by get_dict_data
        today_str = date.today().strftime("%Y%m%d")
        expected_body = {
            "id": 123,
            "user": "test_user",
            "date": today_str
        }

        # Act
        result_config = set_request_body_yaml(config, request_config, body_name)

        # Assert
        # 1. The 'body' key should be correctly set to the processed value.
        assert "body" in result_config
        assert result_config["body"] == expected_body

        # 2. The returned dictionary should be the same object as the one passed in.
        assert result_config is request_config

        # 3. Pre-existing keys in request_config should be preserved.
        assert result_config["existing_key"] == "existing_value"

    def test_raises_key_error_when_body_name_does_not_exist(self):
        """
        Tests that set_request_body_yaml raises a KeyError when body_name
        does not exist in the config dictionary.
        """
        # Arrange
        body_name = "non_existent_body"
        config = {}
        request_config = {}

        # Act & Assert
        with pytest.raises(KeyError) as exc_info:
            set_request_body_yaml(config, request_config, body_name)

        # Assert that the correct key is missing in the error message.
        assert body_name in str(exc_info.value)