import liveramp_automation.utils.testrail
from liveramp_automation.utils.testrail import APIError
from unittest.mock import patch, mock_open, Mock
import pytest

testrail_utils = liveramp_automation.utils.testrail.TestRailUtils()
testrail_utils.suite_config_file = "tests/resources/testrail.yml"
testrail_utils.read_suite_config_file()


def mocked_requests_response(*args, **kwargs):
    response = Mock()
    response.status_code = 200
    response.id = 2
    response.json = Mock(return_value={'id': 3, 'cases': [{'case_id': 29438, 'type_id': 7, 'id': 29438}]})
    return response


def mocked_requests_response_no_json(*args, **kwargs):
    response = Mock()
    response.status_code = 400
    response.id = 2
    response.json = Mock(side_effect=Exception("No JSON object could be decoded"))

    return response


def test_read_configuration():
    print("test")


@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response)
@patch('requests.post', side_effect=mocked_requests_response)
def test_add_run(mock1, mock2, mock3):
    testrail_utils.add_run("smoke")
    assert mock1.call_count == 1
    assert testrail_utils.filtered_case_ids == [29438]


@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response)
@patch('requests.post', side_effect=mocked_requests_response)
def test_add_run_query(mock1, mock2, mock3):
    testrail_utils.add_run("other")
    assert mock1.call_count == 1
    assert mock2.call_count == 1
    assert testrail_utils.filtered_case_ids == [29438]
    assert testrail_utils.include_all == False


# @patch('allure.attach')
# @patch('requests.get', side_effect=mocked_requests_response)
# @patch('requests.post', side_effect=mocked_requests_response)
# def test_add_run_only_suite_data(mock1, mock2,mock3):
#     testrail_utils.add_run("only_suite_data")
#     assert mock1.call_count == 1
#     assert mock2.call_count == 0
#     assert testrail_utils.filtered_case_ids == []
#     assert testrail_utils.include_all is True


@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response)
@patch('requests.post', side_effect=mocked_requests_response)
def test_add_run_no_data(mock1, mock2, mock3):
    with pytest.raises(APIError):
        testrail_utils.add_run("no_data")
        assert mock1.call_count == 1
        assert mock2.call_count == 0
        assert testrail_utils.filtered_case_ids == []
        assert testrail_utils.include_all is True


@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response)
@patch('requests.post', side_effect=mocked_requests_response_no_json)
def test_add_run_invalid_suite(mock1, mock2, mock3):
    with pytest.raises(APIError):
        testrail_utils.filtered_case_ids = [12345]
        testrail_utils.add_run("invalid_suite")
        assert testrail_utils.filtered_case_ids == []


def test_read_file_empty_config():
    with patch('builtins.open', mock_open(read_data="[testrail]")):
        testrail_utils.read_configuration()
        assert testrail_utils.url == 'https://liveramp.testrail.io/index.php?/api/v2/'
        assert testrail_utils.run_url == 'https://liveramp.testrail.io/index.php?/runs/view/'
        assert testrail_utils.report_file == './reports/report.json'


def test_read_file_file_not_found_error():
    with patch('builtins.open', mock_open()) as mock_file:
        mock_file.side_effect = FileNotFoundError()
        testrail_utils.read_configuration()
        assert testrail_utils.url == 'https://liveramp.testrail.io/index.php?/api/v2/'
        assert testrail_utils.run_url == 'https://liveramp.testrail.io/index.php?/runs/view/'
        assert testrail_utils.report_file == './reports/report.json'

    testrail_utils.suite_config_file = "tests/resources/testrail.yml"
    testrail_utils.read_suite_config_file()


def test_get_results_from_report():
    testrail_utils.filtered_case_ids = [29438]
    testrail_utils.report_file = "tests/resources/test.json"
    results = testrail_utils.get_results_from_report()
    assert len(results) == 1
    assert results[0]["case_id"] == 29438


@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response)
@patch('requests.post', side_effect=mocked_requests_response)
def test_upload_results(mock1, mock2, mock3):
    testrail_utils.filtered_case_ids = []
    testrail_utils.upload_results("smoke")
    assert testrail_utils.filtered_case_ids == [29438]
    assert testrail_utils.include_all is False
    assert mock1.call_count == 2
    assert mock2.call_count == 1


# @patch('allure.attach')
# @patch('requests.get', side_effect=mocked_requests_response)
# @patch('requests.post', side_effect=mocked_requests_response)
# def test_upload_results_only_suite_data(mock1, mock2, mock3):
#     testrail_utils.filtered_case_ids = []
#     testrail_utils.upload_results("only_suite_data")
#     assert testrail_utils.filtered_case_ids == []
#     assert testrail_utils.include_all is True
#     assert mock1.call_count == 2
#     assert mock2.call_count == 0


@patch('allure.attach')
@patch('requests.get', side_effect=mocked_requests_response_no_json)
@patch('requests.post', side_effect=mocked_requests_response)
def test_upload_results_error(mock1, mock2, mock3):
    testrail_utils.filtered_case_ids = [29438]
    testrail_utils.upload_results("smoke")
    assert testrail_utils.filtered_case_ids == []
    assert mock1.call_count == 0
    assert mock2.call_count == 1
