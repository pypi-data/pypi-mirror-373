import os
import stat
import tempfile
import shutil
from unittest.mock import patch

from liveramp_automation.helpers.file import FileHelper
import json
import pytest
import tempfile
import yaml
import xml.etree.ElementTree as ET


def mocked_raise_KeyError(*args, **kwargs):
    raise KeyError("KeyError")


def mocked_raise_Exception(*args, **kwargs):
    raise Exception("Exception")


def test_read_init_file():
    file_name = "test.ini"
    ini_file = FileHelper.read_init_file("tests/resources/", file_name)
    assert ini_file


def test_read_json_report_file():
    file_path = "tests/resources/test.json"
    json_str = FileHelper.read_json_report(file_path)
    assert json_str


def test_read_json_report_returns_correct_dictionary():
    file_path = "tests/resources/test.json"
    expected_dict = {"name": "test", "value": 1}

    with patch('json.load', return_value=expected_dict):
        actual_dict = FileHelper.read_json_report(file_path)

    assert actual_dict == expected_dict


def test_read_json_report_file_single_object():
    file_path = "tests/resources/test_single_object.json"
    json_data = FileHelper.read_json_report(file_path)
    assert isinstance(json_data, dict)


def test_load_env_yaml():
    file_prefix = "test"
    env_str = "stg"
    yaml_str = FileHelper.load_env_yaml("tests/resources/", file_prefix, env_str)
    print(yaml_str)
    assert yaml_str


def test_load_env_yaml_path_no_trailing_slash():
    file_prefix = "test"
    env_str = "stg"
    yaml_str = FileHelper.load_env_yaml("tests/resources", file_prefix, env_str)
    print(yaml_str)
    assert yaml_str is not None


def test_load_env_yaml_non_ascii():
    file_prefix = "test_non_ascii"
    env_str = "stg"
    # Create a YAML file with non-ASCII characters
    file_path = os.path.join("tests", "resources", f"{file_prefix}.{env_str}.yaml")
    data = {"name": "测试", "description": "这是一个测试文件"}
    with open(file_path, "w", encoding="utf-8") as f:
        yaml.dump(data, f)

    yaml_str = FileHelper.load_env_yaml("tests/resources/", file_prefix, env_str)
    print(yaml_str)
    assert yaml_str is not None
    assert yaml_str["name"] == "测试"
    assert yaml_str["description"] == "这是一个测试文件"


def test_load_env_yaml_non_dict():
    # Create a YAML file with a non-dictionary root
    file_prefix = "test_non_dict"
    env_str = "stg"
    file_name = f"{file_prefix}.{env_str}.yaml"
    file_path = os.path.join("tests/resources/", file_name)
    scalar_value = "this is not a dictionary"
    with open(file_path, "w") as f:
        yaml.dump(scalar_value, f)

    # Load the YAML file
    loaded_data = FileHelper.load_env_yaml("tests/resources/", file_prefix, env_str)

    # Assert that the loaded data is the scalar value
    assert loaded_data == scalar_value

    # Clean up the created file
    os.remove(file_path)


def test_load_env_yaml_file_not_found():
    file_prefix = "test_not_found"
    env_str = "stg"
    yaml_str = FileHelper.load_env_yaml("tests/resources/", file_prefix, env_str)
    print(yaml_str)
    assert yaml_str is None


def test_load_env_yaml_parse_error():
    file_prefix = "test_parse_error"
    env_str = "stg"
    yaml_str = FileHelper.load_env_yaml("tests/resources/", file_prefix, env_str)
    print(yaml_str)
    assert yaml_str is None


def test_deal_testcase_json():
    file_path = "tests/resources/test.json"
    testcase = FileHelper.read_testcase_json(file_path)
    print(testcase)
    assert testcase


def test_deal_testcase_json_file_not_exist():
    file_path = "tests/resources/test_not_exist.json"
    testcase = FileHelper.read_testcase_json(file_path)
    assert testcase is None


def test_deal_testcase_json_key_not_found():
    file_path = "tests/resources/test_key_not_found.json"
    testcase = FileHelper.read_testcase_json(file_path)
    assert testcase is None


def test_deal_testcase_json_invalid_duration():
    file_path = "tests/resources/test_invalid_duration.json"
    # Create the test file with invalid duration
    test_data = {
        "tests": [
            {
                "nodeid": "test_group/test_class::test_case",
                "outcome": "PASSED",
                "call": {
                    "duration": "abc"
                }
            }
        ]
    }
    with open(file_path, "w") as f:
        json.dump(test_data, f)

    testcase = FileHelper.read_testcase_json(file_path)

    # Clean up the test file
    os.remove(file_path)

    assert testcase is None


def test_deal_testcase_json_empty_tests_array():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix=".json") as temp_file:
        temp_file_path = temp_file.name
        # Write the JSON data with an empty 'tests' array to the temporary file
        json.dump({"tests": []}, temp_file)

    # Call the function with the temporary file path
    testcase = FileHelper.read_testcase_json(temp_file_path)

    # Assert that the function returns None
    assert testcase is None

    # Clean up the temporary file
    os.remove(temp_file_path)


def test_deal_testcase_json_missing_call_crash():
    file_path = "tests/resources/test_missing_call_crash.json"
    # Create a testcase.json file with missing 'call' and 'crash' keys
    test_data = {
        "tests": [
            {
                "nodeid": "test_group/test_class.py::TestClass::test_method",
                "outcome": "FAILED",
            }
        ]
    }
    with open(file_path, "w") as f:
        json.dump(test_data, f)

    testcase = FileHelper.read_testcase_json(file_path)

    # Clean up the created file
    os.remove(file_path)

    assert testcase is None


def test_deal_testcase_json_incorrect_format():
    file_path = "tests/resources/junit.xml"
    testcase = FileHelper.read_testcase_json(file_path)
    assert testcase is None


def test_read_junit_xml_report():
    file_path = "tests/resources/junit.xml"
    testcase = FileHelper.read_junit_xml_report(file_path)
    print(testcase)
    assert testcase


def test_read_junit_xml_report_not_exist():
    file_path = "junit.xml"
    testcase = FileHelper.read_junit_xml_report(file_path)
    assert testcase is None


def test_read_junit_xml_report_file_incorrect_format():
    file_path = "tests/resources/test.json"
    testcase = FileHelper.read_junit_xml_report(file_path)
    assert testcase is None


def test_read_junit_xml_report_missing_attributes():
    # Create a dummy XML file with valid structure but missing attributes
    xml_content = """
    <testsuite>
        <testcase name="test_case_1" classname="class_1"/>
        <testcase name="test_case_2" classname="class_2"/>
    </testsuite>
    """
    file_path = "tests/resources/temp_junit.xml"
    with open(file_path, "w") as f:
        f.write(xml_content)

    # Call the function and assert the result
    result_dict = FileHelper.read_junit_xml_report(file_path)
    expected_dict = {
        "Cases": 0,
        "Failures": 0,
        "Errors": 0,
        "Skipped": 0
    }
    assert result_dict == expected_dict

    # Clean up the temporary file
    import os
    os.remove(file_path)


def test_read_junit_xml_report_non_integer_values():
    # Create a dummy junit.xml file with non-integer values
    xml_content = """
    <testsuite tests="not_an_integer" failures="1" errors="1" skipped="1">
        <testcase classname="test_class" name="test_method"/>
    </testsuite>
    """
    file_path = "tests/resources/temp_junit.xml"
    with open(file_path, "w") as f:
        f.write(xml_content)

    # Call the function and assert that it returns None
    result = FileHelper.read_junit_xml_report(file_path)
    assert result is None

    # Clean up the temporary file
    os.remove(file_path)


def test_read_junit_xml_report_non_integer_values_2():
    # Create a dummy junit.xml file with non-integer values
    xml_content = """
    <testsuite tests="1" failures="not_an_integer" errors="1" skipped="1">
        <testcase classname="test_class" name="test_method"/>
    </testsuite>
    """
    file_path = "tests/resources/temp_junit.xml"
    with open(file_path, "w") as f:
        f.write(xml_content)

    # Call the function and assert that it returns None
    result = FileHelper.read_junit_xml_report(file_path)
    assert result is None

    # Clean up the temporary file
    os.remove(file_path)


def test_read_junit_xml_report_non_integer_values_3():
    # Create a dummy junit.xml file with non-integer values
    xml_content = """
    <testsuite tests="1" failures="1" errors="not_an_integer" skipped="1">
        <testcase classname="test_class" name="test_method"/>
    </testsuite>
    """
    file_path = "tests/resources/temp_junit.xml"
    with open(file_path, "w") as f:
        f.write(xml_content)

    # Call the function and assert that it returns None
    result = FileHelper.read_junit_xml_report(file_path)
    assert result is None

    # Clean up the temporary file
    os.remove(file_path)


def test_read_junit_xml_report_non_integer_values_4():
    # Create a dummy junit.xml file with non-integer values
    xml_content = """
    <testsuite tests="1" failures="1" errors="1" skipped="not_an_integer">
        <testcase classname="test_class" name="test_method"/>
    </testsuite>
    """
    file_path = "tests/resources/temp_junit.xml"
    with open(file_path, "w") as f:
        f.write(xml_content)

    # Call the function and assert that it returns None
    result = FileHelper.read_junit_xml_report(file_path)
    assert result is None

    # Clean up the temporary file
    os.remove(file_path)


@patch('xml.etree.ElementTree.parse', side_effect=mocked_raise_Exception)
def test_read_junit_xml_report_raise_Exception(self):
    file_path = "tests/resources/test.json"
    testcase = FileHelper.read_junit_xml_report(file_path)
    assert testcase is None


@patch('xml.etree.ElementTree.parse', side_effect=mocked_raise_KeyError)
def test_read_junit_xml_report_raise_KeyError(self):
    file_path = "tests/resources/test.json"
    testcase = FileHelper.read_junit_xml_report(file_path)
    assert testcase is None


def test_read_json_report_file_not_exist():
    file_path = "tests/resources/test_not_exist.json"
    return_dict = FileHelper.read_json_report(file_path)
    assert return_dict == {}


def test_read_json_report_file_incorrect_format():
    file_path = "tests/resources/junit.xml"
    return_dict = FileHelper.read_json_report(file_path)
    assert return_dict == {}


def test_read_init_file_not_exist():
    file_name = "file_not_exist.ini"
    ini_file = FileHelper.read_init_file("tests/resources/", file_name)
    assert ini_file == {}


def test_read_init_file_incorrect_format():
    file_name = "test.csv"
    ini_file = FileHelper.read_init_file("tests/resources/", file_name)
    assert ini_file == {}


def test_process_init_line_section_header():
    """
    Tests that _process_init_line correctly sets the current_module and
    initializes a dictionary when a valid section header is provided.
    """
    # Arrange
    line = "[section]"
    current_module = None
    data_dict = {}
    expected_module = "section"
    expected_data_dict = {"section": {}}

    # Act
    new_module = FileHelper._process_init_line(line, current_module, data_dict)

    # Assert
    assert new_module == expected_module
    assert data_dict == expected_data_dict


def test_process_init_line_key_value_pair_with_module():
    """
    Tests that _process_init_line correctly adds a key-value pair to the
    data_dict when a valid key-value pair is provided and current_module is set.
    """
    # Arrange
    line = "key=value"
    current_module = "section"
    data_dict = {"section": {}}
    expected_data_dict = {"section": {"key": "value"}}

    # Act
    new_module = FileHelper._process_init_line(line, current_module, data_dict)

    # Assert
    assert new_module == current_module
    assert data_dict == expected_data_dict


def test_process_init_line_comment_line():
    """
    Tests that _process_init_line returns the current_module and
    does not modify data_dict when the input line is a comment.
    """
    # Arrange
    line = "# This is a comment"
    current_module = "module1"
    data_dict = {"module1": {"key1": "value1"}}
    expected_module = "module1"
    expected_data_dict = {"module1": {"key1": "value1"}}

    # Act
    new_module = FileHelper._process_init_line(line, current_module, data_dict)

    # Assert
    assert new_module == expected_module
    assert data_dict == expected_data_dict


def test_process_init_line_empty_line():
    """
    Tests that _process_init_line returns the current_module and
    does not modify data_dict when the input line is empty.
    """
    # Arrange
    line = ""
    current_module = "module1"
    data_dict = {"module1": {"key1": "value1"}}
    expected_module = "module1"
    expected_data_dict = {"module1": {"key1": "value1"}}

    # Act
    new_module = FileHelper._process_init_line(line, current_module, data_dict)

    # Assert
    assert new_module == expected_module
    assert data_dict == expected_data_dict


def test_process_init_line_multiple_equals():
    """
    Tests that _process_init_line correctly handles lines with multiple '=' characters,
    splitting only on the first occurrence.
    """
    # Arrange
    line = "key=value1=value2=value3"
    current_module = "test_module"
    data_dict = {"test_module": {}}
    expected_data_dict = {"test_module": {"key": "value1=value2=value3"}}

    # Act
    FileHelper._process_init_line(line, current_module, data_dict)

    # Assert
    assert data_dict == expected_data_dict


def test_process_init_line_empty_value():
    """
    Tests that _process_init_line correctly handles a key with an empty value (e.g., 'key=').
    """
    # Arrange
    line = "key="
    current_module = "section"
    data_dict = {"section": {}}
    expected_data_dict = {"section": {"key": ""}}

    # Act
    FileHelper._process_init_line(line, current_module, data_dict)

    # Assert
    assert data_dict == expected_data_dict


def test_process_init_line_key_value_before_section():
    """
    Tests that _process_init_line does not process key-value pairs
    when no section header has been encountered yet (current_module is None).
    """
    # Arrange
    line = "key=value"
    current_module = None
    data_dict = {}
    expected_module = None
    expected_data_dict = {}

    # Act
    new_module = FileHelper._process_init_line(line, current_module, data_dict)

    # Assert
    assert new_module == expected_module
    assert data_dict == expected_data_dict


def test_files_under_folder_with_suffix_xlsx():
    path_string = "tests/resources/"
    file_list = FileHelper.files_under_folder_with_suffix_xlsx(path_string)
    assert file_list == ["test.xlsx"]


def test_files_under_folder_with_suffix_xlsx_absolute_path():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()
    try:
        # Create a dummy xlsx file inside the temporary directory
        file_name = "temp_file.xlsx"
        file_path = os.path.join(temp_dir, file_name)
        open(file_path, 'a').close()

        # Get the absolute path of the temporary directory
        absolute_path = os.path.abspath(temp_dir)

        # Call the function with the absolute path
        file_list = FileHelper.files_under_folder_with_suffix_xlsx(absolute_path)

        # Assert that the file list contains the expected file name
        assert file_list == [file_name]
    finally:
        # Clean up the temporary directory
        shutil.rmtree(temp_dir)


def test_files_under_folder_with_suffix_xlsx_path_is_file():
    # Create a temporary file
    with tempfile.NamedTemporaryFile(suffix=".xlsx") as temp_file:
        file_path = temp_file.name
        # Call the function with the path to the temporary file
        file_list = FileHelper.files_under_folder_with_suffix_xlsx(file_path)
        # Assert that the function returns an empty list
        assert file_list == []


def test_files_under_folder_with_suffix_csv():
    path_string = "tests/resources/"
    file_list = FileHelper.files_under_folder_with_suffix_csv(path_string)
    assert file_list == ["test.csv"]


def test_files_under_folder_with_suffix_csv_absolute_path():
    path_string = os.path.abspath("tests/resources/")
    file_list = FileHelper.files_under_folder_with_suffix_csv(path_string)
    assert file_list == ["test.csv"]


def test_files_under_folder_with_suffix_csv_path_is_file(tmp_path):
    """
    Test that files_under_folder_with_suffix_csv returns an empty list when the path is a file.
    """
    # Create a dummy file
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("dummy content")

    # Patch os.listdir to raise NotADirectoryError
    def mock_listdir(path):
        raise NotADirectoryError(f"Not a directory: {path}")

    with patch("os.listdir", side_effect=mock_listdir):
        file_list = FileHelper.files_under_folder_with_suffix_csv(str(file_path))
        assert file_list == []


def test_files_under_folder_with_suffix_generic():
    path_string = "tests/resources/"
    # Create the test file if it doesn't exist
    file_path = os.path.join(path_string, "test.txt")
    if not os.path.exists(file_path):
        with open(file_path, "w") as f:
            f.write("This is a test file.")

    file_list = FileHelper.files_under_folder_with_suffix(".txt", path_string)
    assert "test.txt" in file_list


def test_files_under_folder_with_suffix_absolute_path():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a temporary file inside the temporary directory
        temp_file_path = os.path.join(tmpdir, "temp_file.txt")
        with open(temp_file_path, "w") as f:
            f.write("This is a temporary file.")

        # Call the function with the absolute path to the temporary directory
        file_list = FileHelper.files_under_folder_with_suffix(".txt", tmpdir)

        # Assert that the function returns a list containing the name of the created file
        assert file_list == ["temp_file.txt"]


def test_files_under_folder_with_suffix_folder_not_exists():
    path_string = "tests/resources/nonexistent_folder/"
    file_list = FileHelper.files_under_folder_with_suffix(".txt", path_string)
    assert file_list == []


def test_files_under_folder_with_suffix_returns_filenames_only():
    # Create a temporary directory
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy file inside the temporary directory
        test_file = os.path.join(tmpdir, "test_file.txt")
        with open(test_file, "w") as f:
            f.write("test content")

        # Call the function under test
        file_list = FileHelper.files_under_folder_with_suffix(".txt", tmpdir)

        # Assert that the returned list contains only the filename, not the full path
        assert file_list == ["test_file.txt"]


def test_files_under_folder_with_suffix_permission_denied():
    # Create a temporary directory
    temp_dir = tempfile.mkdtemp()

    # Deny read permissions to the current user
    os.chmod(temp_dir, stat.S_IWUSR)  # Remove read and execute permissions

    try:
        # Call the function under test
        file_list = FileHelper.files_under_folder_with_suffix(".txt", temp_dir)

        # Assert that the function returns an empty list
        assert file_list == []
    finally:
        # Restore permissions and remove the temporary directory
        os.chmod(temp_dir, stat.S_IRUSR | stat.S_IWUSR | stat.S_IXUSR)  # Restore read, write, and execute permissions
        os.rmdir(temp_dir)


def test_process_init_line_unicode():
    """
    Tests that _process_init_line correctly handles Unicode characters in
    section names and key-value pairs.
    """
    # Arrange
    section_line = "[你好section]"
    key_value_line = "你好key=你好value"
    current_module = None
    data_dict = {}

    # Act
    new_module = FileHelper._process_init_line(section_line, current_module, data_dict)
    FileHelper._process_init_line(key_value_line, new_module, data_dict)

    # Assert
    expected_module = "你好section"
    expected_data_dict = {"你好section": {"你好key": "你好value"}}
    assert new_module == expected_module
    assert data_dict == expected_data_dict


import os
from liveramp_automation.helpers.file import FileHelper


def test_read_init_file_multiple_sections():
    # Create a test .ini file with multiple sections and key-value pairs
    file_path = "tests/resources/"
    file_name = "test_multiple_sections.ini"
    full_path = os.path.join(file_path, file_name)

    # Ensure the test file exists
    with open(full_path, "w") as f:
        f.write("[section1]\n")
        f.write("key1 = value1\n")
        f.write("key2 = value2\n")
        f.write("\n")
        f.write("[section2]\n")
        f.write("key3 = value3\n")
        f.write("key4 = value4\n")

    # Call the function under test
    result = FileHelper.read_init_file(file_path, file_name)

    # Assert that the returned dictionary matches the expected structure and content
    expected_result = {
        "section1": {
            "key1": "value1",
            "key2": "value2"
        },
        "section2": {
            "key3": "value3",
            "key4": "value4"
        }
    }
    assert result == expected_result

    # Clean up the test file
    os.remove(full_path)


import os
from liveramp_automation.helpers.file import FileHelper


def test_read_init_file_with_comments_and_blank_lines():
    # Create the test file
    file_path = "tests/resources/"
    file_name = "test_comments.ini"
    file_content = """
; This is a comment
# This is another comment

[section1]
key1=value1
; Comment within section
key2=value2

[section2]
key3=value3
"""
    os.makedirs(file_path, exist_ok=True)
    with open(os.path.join(file_path, file_name), "w") as f:
        f.write(file_content)

    ini_file = FileHelper.read_init_file(file_path, file_name)
    expected_result = {
        "section1": {
            "key1": "value1",
            "key2": "value2"
        },
        "section2": {
            "key3": "value3"
        }
    }
    assert ini_file == expected_result

    # Clean up the test file
    os.remove(os.path.join(file_path, file_name))


import os
from liveramp_automation.helpers.file import FileHelper


def test_read_init_file_duplicate_sections_and_keys():
    file_path = "tests/resources/"
    file_name = "test_duplicate.ini"
    full_path = os.path.join(file_path, file_name)

    # Create a test .ini file with duplicate sections and keys
    with open(full_path, "w") as f:
        f.write("[section1]\n")
        f.write("key1 = value1\n")
        f.write("key2 = value2\n")
        f.write("[section1]\n")  # Duplicate section
        f.write("key1 = value3\n")  # Duplicate key
        f.write("key3 = value4\n")
        f.write("[section2]\n")
        f.write("key4 = value5\n")
        f.write("[section2]\n")  # Duplicate section
        f.write("key4 = value6\n")  # Duplicate key

    # Call the function to read the .ini file
    ini_file = FileHelper.read_init_file(file_path, file_name)

    # Assert that the dictionary contains the last occurrence of the sections and keys
    expected_dict = {
        "section1": {
            "key1": "value3",
            "key3": "value4"
        },
        "section2": {
            "key4": "value6"
        }
    }

    assert ini_file == expected_dict

    # Clean up the created test file
    os.remove(full_path)


def test_read_init_file_non_ascii():
    file_path = "tests/resources/"
    file_name = "test_non_ascii.ini"
    full_path = os.path.join(file_path, file_name)

    # Create a test file with non-ASCII characters
    with open(full_path, "w") as f:
        f.write("[section]\nkey=value with éàç")

    ini_file = FileHelper.read_init_file(file_path, file_name)

    # Assert that the function correctly reads the non-ASCII characters
    assert ini_file == {'section': {'key': 'value with éàç'}}

    # Clean up the test file
    os.remove(full_path)


def test_read_init_file_key_value_before_section():
    file_path = "tests/resources/"
    file_name = "test_key_value_before_section.ini"
    # Create a test .ini file with key-value pairs before any section
    with open(os.path.join(file_path, file_name), "w") as f:
        f.write("key1 = value1\n")
        f.write("key2 = value2\n")

    ini_file = FileHelper.read_init_file(file_path, file_name)

    # Assert that the function returns an empty dictionary
    assert ini_file == {}

    # Clean up the test file
    os.remove(os.path.join(file_path, file_name))


def test_read_init_file_is_directory(tmpdir):
    """
    Verify that read_init_file returns an empty dictionary when the path is a directory.
    """
    dir_path = tmpdir.mkdir("test_dir")
    file_path = str(dir_path)  # Convert to string to match the expected input type
    file_name = ""  # The function joins file_path and file_name, so file_name can be empty

    ini_file = FileHelper.read_init_file(file_path, file_name)
    assert ini_file == {}


import os
from liveramp_automation.helpers.file import FileHelper


def test_read_init_file_malformed_section_header():
    # Create a test .ini file with a malformed section header
    file_path = "tests/resources/"
    file_name = "test_malformed.ini"
    full_path = os.path.join(file_path, file_name)

    # Create the file if it doesn't exist
    if not os.path.exists(full_path):
        with open(full_path, "w") as f:
            f.write("[section\n")  # Malformed section header
            f.write("key1 = value1\n")
            f.write("[section2]\n")
            f.write("key2 = value2\n")

    # Call the function under test
    ini_file = FileHelper.read_init_file(file_path, file_name)

    # Assert that the resulting dictionary does not contain a section named "section"
    assert "section" not in ini_file

    # Assert that the resulting dictionary contains section2
    assert "section2" in ini_file
    assert ini_file["section2"] == {"key2": "value2"}


import os
import stat
import pytest
from liveramp_automation.helpers.file import FileHelper


def test_read_init_file_permission_error(tmpdir):
    # Create a temporary file
    file_path = tmpdir.join("test.ini")
    file_path.write("test_data")

    # Make the file read-only
    os.chmod(file_path, stat.S_IREAD)

    # Attempt to read the file and assert that an empty dictionary is returned
    ini_file = FileHelper.read_init_file(tmpdir, "test.ini")
    assert ini_file == {}

    # Restore the file permissions (optional, but good practice)
    os.chmod(file_path, stat.S_IWRITE | stat.S_IREAD)