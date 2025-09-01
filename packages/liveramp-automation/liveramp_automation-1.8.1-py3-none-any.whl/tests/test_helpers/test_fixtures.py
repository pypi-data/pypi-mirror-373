import pytest

from unittest.mock import patch


@pytest.fixture(scope="session")
def mock_pytest_ini_file():
    # Mock the os.path.exists method to return True when it's called with the path to the pytest.ini file
    with patch('os.path.exists') as mock_exists:
        mock_exists.return_value = True

        # Mock the FileHelper.read_init_file method to return a predefined dictionary
        with patch('liveramp_automation.helpers.file.FileHelper.read_init_file') as mock_read_init_file:
            mock_read_init_file.return_value = {
                'data': {
                    'resource_path': 'tests/resources',
                    'resource_prefix': 'res'
                }
            }

# The following Unit test case is not working
# def test_res(res):
#     pass
    # Check if res is a dictionary
    # assert isinstance(res, dict), "res should return a dictionary"
    # # Check if the keys exist in the dictionary
    # assert 'queryTable' in res, "res should have a key named 'queryTable'"
    # # Check the type of the values
    # assert isinstance(res['queryTable'], str), "The value of 'queryTable' should be a string"
