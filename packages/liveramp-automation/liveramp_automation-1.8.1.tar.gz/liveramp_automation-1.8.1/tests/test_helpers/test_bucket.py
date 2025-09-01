from liveramp_automation.helpers.bucket import BucketHelper
from liveramp_automation.utils.time import MACROS
from unittest.mock import patch

project_id = "liveramp-eng-qa-reliability"
bucket_name = "liveramp_automation_test"
file = "../resources/test.ini"
download_folder = "reports"
download_folder_1 = "reports/001"
download_folder_2 = "reports/002"
number_lines = 3
search_by_string = "test_download"
source_file_path = "tests"
source_file_name = "tests/test_utils/test_selenium.py"
destination_blob_name = "{}_UnitTest".format("{now}".format(**MACROS))
destination_blob_path_filename = "Unit/UnitTestFileSample.log"
bucket_helper = BucketHelper(project_id, bucket_name)
file_helper = BucketHelper(project_id, bucket_name)


def test_upload_files():
    bucket_helper.upload_file(source_file_path, destination_blob_name)


def test_upload_file():
    bucket_helper.upload_file(source_file_name, destination_blob_name)


def test_check_file_exists():
    result = bucket_helper.check_file_exists(destination_blob_path_filename)
    assert result


def test_download_files():
    result = bucket_helper.download_files(destination_blob_name, download_folder_1)
    assert result


def mocked_requests_response_throw_exception(*args, **kwargs):
    raise Exception("Test")


@patch('liveramp_automation.utils.log.Logger.info', side_effect=mocked_requests_response_throw_exception)
def test_download_files_exception(mock):
    result = bucket_helper.download_files(destination_blob_name, download_folder_1)
    assert len(result) == 0


def test_download_files_with_structure():
    result = bucket_helper.download_files_with_structure(destination_blob_name, download_folder_2)
    assert result


def test_download_file():
    result = bucket_helper.download_files(destination_blob_path_filename, download_folder)
    assert result


def test_list_files_with_substring():
    result = bucket_helper.list_files_with_substring(search_by_string)
    assert result


def test_get_total_rows():
    result = bucket_helper.get_total_rows(destination_blob_path_filename)
    assert result


def test_read_file_content():
    result = bucket_helper.read_file_content(destination_blob_path_filename)
    assert result


def test_read_file_lines():
    result = bucket_helper.read_file_lines(destination_blob_path_filename, number_lines)
    assert result
