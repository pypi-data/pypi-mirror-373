import pytest
from unittest.mock import patch, MagicMock

from liveramp_automation.utils.report import reportUtils
from liveramp_automation.utils.log import Logger  # Import Logger


@pytest.fixture
def report_utils_instance():
    """Provides a clean instance of reportUtils for each test."""
    instance = reportUtils()
    # Set up table references, as this is a prerequisite for the function under test.
    instance.bigquery_ref_tables(
        project_id="test-project",
        dataset_id="test-dataset",
        round_table="test_round_table",
        feature_table="test_feature_table",
        scenario_table="test_scenario_table",
        step_table="test_step_table"
    )
    return instance


@pytest.fixture
def valid_cucumber_report_data():
    """Provides a valid cucumber JSON report structure for happy path testing."""
    return [
        {
            "keyword": "Feature",
            "uri": "features/test.feature",
            "id": "test-feature",
            "line": 1,
            "name": "Test Feature",
            "description": "A description for the test feature.",
            "elements": [
                {
                    "keyword": "Scenario",
                    "id": "test-feature;test-scenario",
                    "line": 3,
                    "name": "Test Scenario",
                    "description": "A test scenario.",
                    "tags": [{"name": "tag1"}, {"name": "smoke"}],
                    "type": "scenario",
                    "steps": [
                        {
                            "keyword": "Given ",
                            "name": "a passing step",
                            "line": 4,
                            "match": {"location": "features/steps/test_steps.py:10"},
                            "result": {"status": "passed", "duration": 0.1}
                        }
                    ]
                }
            ]
        }
    ]


@pytest.fixture
def malformed_cucumber_report_data():
    """Provides malformed cucumber report data with a missing 'id' field."""
    return [
        {
            "keyword": "Feature",
            "uri": "features/test.feature",
            "line": 1,
            "name": "Test Feature",
            "description": "A description for the test feature.",
            "elements": []
        }
    ]


@pytest.fixture
def cucumber_report_data_with_failed_step():
    """Provides cucumber JSON report data with a failed step."""
    return [
        {
            "keyword": "Feature",
            "uri": "features/test.feature",
            "id": "test-feature",
            "line": 1,
            "name": "Test Feature",
            "description": "A description for the test feature.",
            "elements": [
                {
                    "keyword": "Scenario",
                    "id": "test-feature;test-scenario",
                    "line": 3,
                    "name": "Test Scenario",
                    "description": "A test scenario.",
                    "tags": [{"name": "tag1"}, {"name": "smoke"}],
                    "type": "scenario",
                    "steps": [
                        {
                            "keyword": "Given ",
                            "name": "a failing step",
                            "line": 4,
                            "match": {"location": "features/steps/test_steps.py:10"},
                            "result": {"status": "failed", "duration": 0.1}
                        }
                    ]
                }
            ]
        }
    ]


@pytest.fixture
def feature_with_multiple_scenarios():
    """Provides a feature dictionary with multiple scenarios and steps for testing."""
    return {
        "elements": [
            {
                "id": "my-feature;scenario-1",
                "name": "First Scenario",
                "description": "This is the first test scenario.",
                "line": 5,
                "keyword": "Scenario",
                "tags": [{"name": "smoke"}, {"name": "regression"}],
                "steps": [
                    {
                        "name": "a user is logged in",
                        "keyword": "Given ",
                        "line": 6,
                        "result": {"status": "passed", "duration": 100},
                        "match": {"location": "steps.py:10"}
                    },
                    {
                        "name": "the user clicks the button",
                        "keyword": "When ",
                        "line": 7,
                        "result": {"status": "passed", "duration": 200},
                        "match": {"location": "steps.py:11"}
                    }
                ]
            },
            {
                "id": "my-feature;scenario-2",
                "name": "Second Scenario",
                "description": "This is the second test scenario.",
                "line": 10,
                "keyword": "Scenario",
                "tags": [{"name": "core"}],
                "steps": [
                    {
                        "name": "something happens",
                        "keyword": "Then ",
                        "line": 11,
                        "result": {"status": "failed", "duration": 300, "error_message": "Assertion failed"},
                        "match": {"location": "steps.py:20"}
                    }
                ]
            }
        ]
    }


@pytest.fixture
def feature_with_scenario_missing_tags():
    """Provides a feature dictionary with a scenario that is missing the 'tags' key."""
    return {
        "elements": [
            {
                "id": "my-feature;scenario-no-tags",
                "name": "Scenario without Tags",
                "description": "This scenario does not have tags.",
                "line": 5,
                "keyword": "Scenario",
                "steps": [
                    {
                        "name": "a step is executed",
                        "keyword": "Given ",
                        "line": 6,
                        "result": {"status": "passed", "duration": 100},
                        "match": {"location": "steps.py:10"}
                    }
                ]
                # 'tags' key is intentionally missing
            }
        ]
    }


def test_insert_from_pytest_bdd_cucumber_report_success(report_utils_instance, valid_cucumber_report_data):
    """
    Tests the happy path where the cucumber report is valid and all BigQuery inserts succeed.
    The function should process the data and return 0.
    """
    with patch('liveramp_automation.utils.report.FileHelper.read_json_report',
               return_value=valid_cucumber_report_data) as mock_read_json, \
         patch('liveramp_automation.utils.report.bigquery.Client') as mock_bigquery_client, \
         patch.dict('os.environ', {'ENVCHOICE': 'TEST', 'PRODUCTNAME': 'TEST_PRODUCT'}, clear=True):

        # Configure the mock BigQuery client to simulate successful API calls
        mock_client_instance = mock_bigquery_client.return_value
        mock_client_instance.get_table.return_value = MagicMock()
        mock_client_instance.insert_rows.return_value = []  # Empty list signifies success

        # Act: Call the function under test
        result = report_utils_instance.insert_from_pytest_bdd_cucumber_report()

        # Assert: Verify the function returned the success code
        assert result == 0

        # Assert: Verify dependencies were called as expected
        mock_read_json.assert_called_once_with(report_utils_instance.report_cucumber_path)
        mock_bigquery_client.assert_called_once()

        # Assert: Verify that data was inserted into all four tables
        assert mock_client_instance.insert_rows.call_count == 4

        # Assert: Verify the content of the data sent to BigQuery
        calls = mock_client_instance.insert_rows.call_args_list
        round_rows = calls[0].args[1]
        feature_rows = calls[1].args[1]
        scenario_rows = calls[2].args[1]
        step_rows = calls[3].args[1]

        assert len(round_rows) == 1
        assert round_rows[0]['round_execution_env'] == 'TEST'
        assert round_rows[0]['round_suite_name'] == 'TEST_PRODUCT'
        assert round_rows[0]['round_execution_result'] == 'PASS'
        assert round_rows[0]['round_scenario_count'] == 1
        assert round_rows[0]['round_step_failed_count'] == 0

        assert len(feature_rows) == 1
        assert feature_rows[0]['feature_name'] == 'Test Feature'

        assert len(scenario_rows) == 1
        assert scenario_rows[0]['scenario_name'] == 'Test Scenario'
        assert scenario_rows[0]['scenario_tags'] == 'tag1,smoke'

        assert len(step_rows) == 1
        assert step_rows[0]['step_name'] == 'a passing step'
        assert step_rows[0]['step_status'] == 'passed'
        assert 'step_scenario_id' not in step_rows[0]  # Verify field was removed before insert


def test_insert_from_pytest_bdd_cucumber_report_empty_report(report_utils_instance):
    """
    Tests the scenario where FileHelper.read_json_report returns an empty dict.
    The function should return -1, indicating no data to process.
    """
    with patch('liveramp_automation.utils.report.FileHelper.read_json_report', return_value={}) as mock_read_json, \
            patch('liveramp_automation.utils.report.bigquery.Client') as mock_bigquery_client:
        # Act: Call the function under test
        result = report_utils_instance.insert_from_pytest_bdd_cucumber_report()

        # Assert: Verify the function returned the expected error code
        assert result == -1

        # Assert: Verify that read_json_report was called
        mock_read_json.assert_called_once_with(report_utils_instance.report_cucumber_path)

        # Assert: Verify that bigquery client was not called, as the report was empty
        mock_bigquery_client.assert_not_called()


def test_insert_from_pytest_bdd_cucumber_report_missing_step_scenario_id(report_utils_instance):
    """
    Tests the scenario where a step is missing the 'step_scenario_id' field.
    The function should handle this gracefully and not raise a KeyError.
    """
    cucumber_report_data = [
        {
            "keyword": "Feature",
            "uri": "features/test.feature",
            "id": "test-feature",
            "line": 1,
            "name": "Test Feature",
            "description": "A description for the test feature.",
            "elements": [
                {
                    "keyword": "Scenario",
                    "id": "test-feature;test-scenario",
                    "line": 3,
                    "name": "Test Scenario",
                    "description": "A test scenario.",
                    "tags": [{"name": "tag1"}, {"name": "smoke"}],
                    "type": "scenario",
                    "steps": [
                        {
                            "keyword": "Given ",
                            "name": "a passing step",
                            "line": 4,
                            "match": {"location": "features/steps/test_steps.py:10"},
                            "result": {"status": "passed", "duration": 0.1}
                        },
                        {
                            "keyword": "When ",
                            "name": "another step",
                            "line": 5,
                            "match": {"location": "features/steps/test_steps.py:15"},
                            "result": {"status": "passed", "duration": 0.2},
                            # Missing 'step_scenario_id' field
                        }
                    ]
                }
            ]
        }
    ]

    with patch('liveramp_automation.utils.report.FileHelper.read_json_report',
               return_value=cucumber_report_data) as mock_read_json, \
         patch('liveramp_automation.utils.report.bigquery.Client') as mock_bigquery_client, \
         patch.dict('os.environ', {'ENVCHOICE': 'TEST', 'PRODUCTNAME': 'TEST_PRODUCT'}, clear=True):

        # Configure the mock BigQuery client to simulate successful API calls
        mock_client_instance = mock_bigquery_client.return_value
        mock_client_instance.get_table.return_value = MagicMock()
        mock_client_instance.insert_rows.return_value = []  # Empty list signifies success

        # Act: Call the function under test
        result = report_utils_instance.insert_from_pytest_bdd_cucumber_report()

        # Assert: Verify the function returned the success code
        assert result == 0

        # Assert: Verify dependencies were called as expected
        mock_read_json.assert_called_once_with(report_utils_instance.report_cucumber_path)
        mock_bigquery_client.assert_called_once()

        # Assert: Verify that data was inserted into all four tables
        assert mock_client_instance.insert_rows.call_count == 4


def test_insert_from_pytest_bdd_cucumber_report_failed_step(report_utils_instance, cucumber_report_data_with_failed_step):
    """
    Tests the scenario where a step has a failed status.
    The function should increment failed_count and update failed_step_id.
    """
    with patch('liveramp_automation.utils.report.FileHelper.read_json_report',
               return_value=cucumber_report_data_with_failed_step) as mock_read_json, \
         patch('liveramp_automation.utils.report.bigquery.Client') as mock_bigquery_client, \
         patch.dict('os.environ', {'ENVCHOICE': 'TEST', 'PRODUCTNAME': 'TEST_PRODUCT'}, clear=True):

        # Configure the mock BigQuery client to simulate successful API calls
        mock_client_instance = mock_bigquery_client.return_value
        mock_client_instance.get_table.return_value = MagicMock()
        mock_client_instance.insert_rows.return_value = []  # Empty list signifies success

        # Act: Call the function under test
        result = report_utils_instance.insert_from_pytest_bdd_cucumber_report()

        # Assert: Verify the function returned the success code
        assert result == 0

        # Assert: Verify dependencies were called as expected
        mock_read_json.assert_called_once_with(report_utils_instance.report_cucumber_path)
        mock_bigquery_client.assert_called_once()

        # Assert: Verify that data was inserted into all four tables
        assert mock_client_instance.insert_rows.call_count == 4

        # Assert: Verify the content of the data sent to BigQuery
        calls = mock_client_instance.insert_rows.call_args_list
        round_rows = calls[0].args[1]

        assert len(round_rows) == 1
        assert round_rows[0]['round_step_failed_count'] == 1
        assert round_rows[0]['round_execution_result'] == 'FAIL'


def test_insert_from_pytest_bdd_cucumber_report_round_table_insertion_failure(report_utils_instance, valid_cucumber_report_data):
    """
    Tests the scenario where the insertion into the round_table fails.
    The function should return -1.
    """
    with patch('liveramp_automation.utils.report.FileHelper.read_json_report',
               return_value=valid_cucumber_report_data) as mock_read_json, \
         patch('liveramp_automation.utils.report.bigquery.Client') as mock_bigquery_client, \
         patch.object(Logger, 'error') as mock_logger:

        # Configure the mock BigQuery client to simulate a failure when inserting into round_table
        mock_client_instance = mock_bigquery_client.return_value
        mock_client_instance.get_table.return_value = MagicMock()
        mock_client_instance.insert_rows.side_effect = [
            [{'errors': 'some error'}],  # Simulate error for round_table
            [],  # Success for feature_table
            [],  # Success for scenario_table
            []   # Success for step_table
        ]

        # Act: Call the function under test
        result = report_utils_instance.insert_from_pytest_bdd_cucumber_report()

        # Assert: Verify the function returned the error code
        assert result == -1

        # Assert: Verify dependencies were called as expected
        mock_read_json.assert_called_once_with(report_utils_instance.report_cucumber_path)
        mock_bigquery_client.assert_called_once()
        mock_logger.assert_called_once()  # Ensure logger.error was called


def test_insert_from_pytest_bdd_cucumber_report_scenario_table_insertion_failure(report_utils_instance, valid_cucumber_report_data):
    """
    Tests the scenario where inserting data into the scenario_table fails.
    The function should return -1.
    """
    with patch('liveramp_automation.utils.report.FileHelper.read_json_report',
               return_value=valid_cucumber_report_data) as mock_read_json, \
         patch('liveramp_automation.utils.report.bigquery.Client') as mock_bigquery_client, \
         patch('liveramp_automation.utils.report.Logger.error') as mock_logger, \
         patch.dict('os.environ', {'ENVCHOICE': 'TEST', 'PRODUCTNAME': 'TEST_PRODUCT'}, clear=True):

        # Configure the mock BigQuery client to simulate successful API calls for round and feature tables,
        # but simulate failure for scenario table.
        mock_client_instance = mock_bigquery_client.return_value
        mock_client_instance.get_table.return_value = MagicMock()
        mock_client_instance.insert_rows.side_effect = [
            [],  # Simulate success for round_table
            [],  # Simulate success for feature_table
            ["Scenario table insertion failed"],  # Simulate failure for scenario_table
        ]

        # Act: Call the function under test
        result = report_utils_instance.insert_from_pytest_bdd_cucumber_report()

        # Assert: Verify the function returned the error code
        assert result == -1

        # Assert: Verify the logger was called with an error message
        mock_logger.assert_called_once_with('Scenario table errors: [\'Scenario table insertion failed\']')

        # Assert: Verify dependencies were called as expected
        mock_read_json.assert_called_once_with(report_utils_instance.report_cucumber_path)
        mock_bigquery_client.assert_called_once()

        # Assert: Verify that insert_rows was called three times (round, feature, scenario) before the exception
        assert mock_client_instance.insert_rows.call_count == 3


def test_insert_from_pytest_bdd_cucumber_report_feature_table_insertion_failure(report_utils_instance, valid_cucumber_report_data):
    """
    Tests the scenario where insertion into the feature_table fails.
    The function should return -1 and log an error.
    """
    with patch('liveramp_automation.utils.report.FileHelper.read_json_report',
               return_value=valid_cucumber_report_data) as mock_read_json, \
         patch('liveramp_automation.utils.report.bigquery.Client') as mock_bigquery_client, \
         patch.object(Logger, 'error') as mock_logger_error:

        # Configure the mock BigQuery client to simulate a successful round_table insertion
        # and a failed feature_table insertion.
        mock_client_instance = mock_bigquery_client.return_value
        mock_client_instance.get_table.return_value = MagicMock()
        mock_client_instance.insert_rows.side_effect = [
            [],  # Simulate successful round_table insertion
            ['error']  # Simulate failed feature_table insertion
        ]

        # Act: Call the function under test
        result = report_utils_instance.insert_from_pytest_bdd_cucumber_report()

        # Assert: Verify the function returned the error code
        assert result == -1

        # Assert: Verify dependencies were called as expected
        mock_read_json.assert_called_once_with(report_utils_instance.report_cucumber_path)
        mock_bigquery_client.assert_called_once()

        # Assert: Verify that insert_rows was called twice (round_table and feature_table)
        assert mock_client_instance.insert_rows.call_count == 2

        # Assert: Verify that Logger.error was called with the expected error message
        mock_logger_error.assert_called_once_with('Feature Table errors: [\'error\']')


def test_insert_from_pytest_bdd_cucumber_report_step_table_insertion_failure(report_utils_instance, valid_cucumber_report_data):
    """
    Tests the scenario where inserting rows into the step_table fails.
    The function should return -1 and log an error.
    """
    with patch('liveramp_automation.utils.report.FileHelper.read_json_report',
               return_value=valid_cucumber_report_data) as mock_read_json, \
         patch('liveramp_automation.utils.report.bigquery.Client') as mock_bigquery_client, \
         patch.object(Logger, 'error') as mock_logger_error, \
         patch.dict('os.environ', {'ENVCHOICE': 'TEST', 'PRODUCTNAME': 'TEST_PRODUCT'}, clear=True):

        # Configure the mock BigQuery client to simulate successful API calls for round, feature, and scenario tables,
        # but a failed API call for the step table.
        mock_client_instance = mock_bigquery_client.return_value
        mock_client_instance.get_table.return_value = MagicMock()
        mock_client_instance.insert_rows.side_effect = [[], [], [], ['an error']]

        # Act: Call the function under test
        result = report_utils_instance.insert_from_pytest_bdd_cucumber_report()

        # Assert: Verify the function returned the error code
        assert result == -1

        # Assert: Verify dependencies were called as expected
        mock_read_json.assert_called_once_with(report_utils_instance.report_cucumber_path)
        mock_bigquery_client.assert_called_once()

        # Assert: Verify that data was attempted to be inserted into all four tables
        assert mock_client_instance.insert_rows.call_count == 4

        # Assert that Logger.error was called with the expected message
        mock_logger_error.assert_called_with("Step Table errors: ['an error']")


@patch('google.cloud.bigquery.Client')
def test_insert_from_pytest_bdd_cucumber_report_malformed_feature(mock_client, report_utils_instance, malformed_cucumber_report_data):
    """
    Tests that a KeyError is raised when the cucumber report contains malformed feature data
    (e.g., missing 'id' field).
    """
    with patch('liveramp_automation.utils.report.FileHelper.read_json_report',
               return_value=malformed_cucumber_report_data):
        with pytest.raises(KeyError) as excinfo:
            report_utils_instance.insert_from_pytest_bdd_cucumber_report()
        assert "id" in str(excinfo.value)


def test_get_scenarios_steps_from_feature_happy_path_multiple_scenarios(
    report_utils_instance, feature_with_multiple_scenarios
):
    """
    Tests that _get_scenarios_steps_from_feature_ correctly processes a feature
    with multiple scenarios, generating the correct scenario and step rows.
    """
    unique_round_id = "test-round-123"
    mock_uuids = [
        "scenario-uuid-1", "step-uuid-1-1", "step-uuid-1-2",
        "scenario-uuid-2", "step-uuid-2-1"
    ]
    mock_timestamp = "2023-10-27 10:00:00"

    with patch('liveramp_automation.utils.report.uuid.uuid4', side_effect=lambda: mock_uuids.pop(0)), \
         patch.dict('liveramp_automation.utils.report.MACROS', {'now_readable': mock_timestamp}):

        # Act
        scenarios, steps = report_utils_instance._get_scenarios_steps_from_feature_(
            feature_with_multiple_scenarios, unique_round_id
        )

        # Assert
        # Verify counts
        assert len(scenarios) == 2
        assert len(steps) == 3

        # Verify first scenario
        scenario1 = scenarios[0]
        assert scenario1["id"] == "scenario-uuid-1"
        assert scenario1["scenario_round_id"] == unique_round_id
        assert scenario1["scenario_id"] == "my-feature;scenario-1"
        assert scenario1["scenario_name"] == "First Scenario"
        assert scenario1["scenario_description"] == "This is the first test scenario."
        assert scenario1["scenario_line"] == 5
        assert scenario1["scenario_keyword"] == "Scenario"
        assert scenario1["scenario_timestamp"] == mock_timestamp
        assert scenario1["scenario_tags"] == "smoke,regression"
        assert scenario1["scenario_steps"] == "step-uuid-1-1,step-uuid-1-2"

        # Verify second scenario
        scenario2 = scenarios[1]
        assert scenario2["id"] == "scenario-uuid-2"
        assert scenario2["scenario_round_id"] == unique_round_id
        assert scenario2["scenario_id"] == "my-feature;scenario-2"
        assert scenario2["scenario_name"] == "Second Scenario"
        assert scenario2["scenario_tags"] == "core"
        assert scenario2["scenario_steps"] == "step-uuid-2-1"

        # Verify aggregated steps
        step1_1, step1_2, step2_1 = steps[0], steps[1], steps[2]

        assert step1_1["id"] == "step-uuid-1-1"
        assert step1_1["step_scenario_id"] == "my-feature;scenario-1"
        assert step1_1["step_name"] == "a user is logged in"
        assert step1_1["step_status"] == "passed"

        assert step1_2["id"] == "step-uuid-1-2"
        assert step1_2["step_scenario_id"] == "my-feature;scenario-1"
        assert step1_2["step_name"] == "the user clicks the button"

        assert step2_1["id"] == "step-uuid-2-1"
        assert step2_1["step_scenario_id"] == "my-feature;scenario-2"
        assert step2_1["step_name"] == "something happens"
        assert step2_1["step_status"] == "failed"
        assert step2_1["step_error_message"] == "Assertion failed"


def test_get_scenarios_steps_from_feature_empty_steps(report_utils_instance):
    """
    Tests that _get_scenarios_steps_from_feature_ correctly handles a scenario
    with no steps (empty steps list).
    """
    feature = {
        "elements": [
            {
                "id": "my-feature;scenario-1",
                "name": "First Scenario",
                "description": "This is the first test scenario.",
                "line": 5,
                "keyword": "Scenario",
                "tags": [{"name": "smoke"}, {"name": "regression"}],
                "steps": []  # Empty steps list
            }
        ]
    }
    unique_round_id = "test-round-123"
    mock_uuid = "scenario-uuid-1"
    mock_timestamp = "2023-10-27 10:00:00"

    with patch('liveramp_automation.utils.report.uuid.uuid4', return_value=mock_uuid), \
         patch.dict('liveramp_automation.utils.report.MACROS', {'now_readable': mock_timestamp}):
        # Act
        scenarios, steps = report_utils_instance._get_scenarios_steps_from_feature_(feature, unique_round_id)

        # Assert
        assert len(scenarios) == 1
        assert len(steps) == 0

        scenario = scenarios[0]
        assert scenario["scenario_steps"] == ""


def test_get_scenarios_steps_from_feature_missing_tags(
    report_utils_instance, feature_with_scenario_missing_tags
):
    """
    Tests that _get_scenarios_steps_from_feature_ raises a KeyError when a scenario
    is missing the 'tags' key.
    """
    unique_round_id = "test-round-123"
    mock_uuid = "scenario-uuid-1"
    mock_timestamp = "2023-10-27 10:00:00"

    with patch('liveramp_automation.utils.report.uuid.uuid4', return_value=mock_uuid), \
         patch.dict('liveramp_automation.utils.report.MACROS', {'now_readable': mock_timestamp}), \
         pytest.raises(KeyError):
        report_utils_instance._get_scenarios_steps_from_feature_(
            feature_with_scenario_missing_tags, unique_round_id
        )


def test_get_scenarios_steps_from_feature_invalid_data_types(report_utils_instance):
    """
    Tests that _get_scenarios_steps_from_feature_ handles scenarios with
    unexpected data types for required fields without raising exceptions.
    """
    feature = {
        "elements": [
            {
                "id": "my-feature;scenario-1",
                "name": 123,  # Invalid data type
                "description": {"key": "value"},  # Invalid data type
                "line": "abc",  # Invalid data type
                "keyword": ["Scenario"],  # Invalid data type
                "tags": [{"name": "smoke"}],
                "steps": []
            }
        ]
    }
    unique_round_id = "test-round-123"
    mock_uuid = "scenario-uuid-1"
    mock_timestamp = "2023-10-27 10:00:00"

    with patch('liveramp_automation.utils.report.uuid.uuid4', return_value=mock_uuid), \
         patch.dict('liveramp_automation.utils.report.MACROS', {'now_readable': mock_timestamp}):
        # Act
        scenarios, steps = report_utils_instance._get_scenarios_steps_from_feature_(feature, unique_round_id)

        # Assert
        assert len(scenarios) == 1
        scenario = scenarios[0]
        assert scenario["scenario_name"] == 123
        assert scenario["scenario_description"] == {"key": "value"}
        assert scenario["scenario_line"] == "abc"
        assert scenario["scenario_keyword"] == ["Scenario"]


def test_get_steps_from_scenario_happy_path_multiple_steps(report_utils_instance):
    """
    Tests _get_steps_from_scenario_ with a scenario containing multiple, well-formed steps.
    It should return a list of step row dictionaries with all fields correctly mapped.
    """
    # Arrange
    unique_id = "test-round-uuid-123"
    scenario = {
        "id": "test-scenario-id-456",
        "steps": [
            {
                "name": "Given a user is logged in",
                "keyword": "Given ",
                "line": 10,
                "match": {"location": "features/steps/auth.py:15"},
                "result": {"status": "passed", "duration": 100.5}
            },
            {
                "name": "When the user navigates to the dashboard",
                "keyword": "When ",
                "line": 11,
                "match": {"location": "features/steps/navigation.py:20"},
                "result": {"status": "failed", "duration": 250.0}
            }
        ]
    }
    mock_uuids = ["step-uuid-1", "step-uuid-2"]
    mock_timestamp = "2023-10-27 10:00:00"

    with patch('liveramp_automation.utils.report.uuid.uuid4', side_effect=mock_uuids) as mock_uuid, \
         patch.dict('liveramp_automation.utils.report.MACROS', {'now_readable': mock_timestamp}):

        # Act
        result_steps = report_utils_instance._get_steps_from_scenario_(scenario, unique_id)

        # Assert
        assert len(result_steps) == 2
        assert mock_uuid.call_count == 2

        # Assertions for the first step (passed)
        step1 = result_steps[0]
        assert step1['id'] == "step-uuid-1"
        assert step1['step_scenario_id'] == "test-scenario-id-456"
        assert step1['step_round_id'] == unique_id
        assert step1['step_name'] == "Given a user is logged in"
        assert step1['step_keyword'] == "Given "
        assert step1['step_line'] == 10
        assert step1['step_status'] == "passed"
        assert step1['step_duration'] == 100.5
        assert step1['step_location'] == "features/steps/auth.py:15"
        assert step1['step_timestamp'] == mock_timestamp
        assert 'step_error_message' not in step1

        # Assertions for the second step (failed)
        step2 = result_steps[1]
        assert step2['id'] == "step-uuid-2"
        assert step2['step_scenario_id'] == "test-scenario-id-456"
        assert step2['step_round_id'] == unique_id
        assert step2['step_name'] == "When the user navigates to the dashboard"
        assert step2['step_keyword'] == "When "
        assert step2['step_line'] == 11
        assert step2['step_status'] == "failed"
        assert step2['step_duration'] == 250.0
        assert step2['step_location'] == "features/steps/navigation.py:20"
        assert step2['step_timestamp'] == mock_timestamp
        assert 'step_error_message' not in step2


def test_get_steps_from_scenario_defaults_step_status_to_passed_when_status_key_missing(report_utils_instance):
    """
    Tests that _get_steps_from_scenario_ sets 'step_status' to 'passed'
    when step['result'] does not contain a 'status' key.
    """
    # Arrange
    unique_id = "test-round-uuid-123"
    scenario = {
        "id": "test-scenario-id-456",
        "steps": [
            {
                "name": "Given a user is logged in",
                "keyword": "Given ",
                "line": 10,
                "match": {"location": "features/steps/auth.py:15"},
                "result": {"duration": 100.5}  # Missing 'status' key
            }
        ]
    }
    mock_uuid = "step-uuid-1"
    mock_timestamp = "2023-10-27 10:00:00"

    with patch('liveramp_automation.utils.report.uuid.uuid4', return_value=mock_uuid) as mock_uuid_func, \
         patch.dict('liveramp_automation.utils.report.MACROS', {'now_readable': mock_timestamp}):
        # Act
        result_steps = report_utils_instance._get_steps_from_scenario_(scenario, unique_id)

        # Assert
        assert len(result_steps) == 1
        step = result_steps[0]
        assert step['step_status'] == "passed"
        assert step['id'] == "step-uuid-1"
        assert step['step_scenario_id'] == "test-scenario-id-456"
        assert step['step_round_id'] == unique_id
        assert step['step_name'] == "Given a user is logged in"
        assert step['step_keyword'] == "Given "
        assert step['step_line'] == 10
        assert step['step_duration'] == 100.5
        assert step['step_location'] == "features/steps/auth.py:15"
        assert step['step_timestamp'] == mock_timestamp
        assert 'step_error_message' not in step


def test_get_steps_from_scenario_includes_error_message(report_utils_instance):
    """
    Tests that _get_steps_from_scenario_ includes 'step_error_message' in the step row
    if step['result'] contains an 'error_message' key.
    """
    # Arrange
    unique_id = "test-round-uuid-123"
    scenario = {
        "id": "test-scenario-id-456",
        "steps": [
            {
                "name": "Given a failing step",
                "keyword": "Given ",
                "line": 10,
                "match": {"location": "features/steps/failing.py:15"},
                "result": {
                    "status": "failed",
                    "duration": 100.5,
                    "error_message": "Assertion failed: Expected X but got Y"
                }
            }
        ]
    }
    mock_uuid = "step-uuid-1"
    mock_timestamp = "2023-10-27 10:00:00"

    with patch('liveramp_automation.utils.report.uuid.uuid4', return_value=mock_uuid) as mock_uuid_func, \
         patch.dict('liveramp_automation.utils.report.MACROS', {'now_readable': mock_timestamp}):
        # Act
        result_steps = report_utils_instance._get_steps_from_scenario_(scenario, unique_id)

        # Assert
        assert len(result_steps) == 1
        step = result_steps[0]
        assert step['step_error_message'] == "Assertion failed: Expected X but got Y"
        assert step['id'] == "step-uuid-1"
        assert step['step_scenario_id'] == "test-scenario-id-456"
        assert step['step_round_id'] == unique_id
        assert step['step_name'] == "Given a failing step"
        assert step['step_keyword'] == "Given "
        assert step['step_line'] == 10
        assert step['step_status'] == "failed"
        assert step['step_duration'] == 100.5
        assert step['step_location'] == "features/steps/failing.py:15"
        assert step['step_timestamp'] == mock_timestamp


def test_get_steps_from_scenario_sets_step_timestamp(report_utils_instance):
    """
    Tests that _get_steps_from_scenario_ sets 'step_timestamp' to MACROS['now_readable'] for every step.
    """
    # Arrange
    unique_id = "test-round-uuid"
    scenario = {
        "id": "test-scenario-id",
        "steps": [
            {
                "name": "Step 1",
                "keyword": "Given",
                "line": 1,
                "match": {"location": "file1.py:1"},
                "result": {"status": "passed", "duration": 1.0}
            },
            {
                "name": "Step 2",
                "keyword": "When",
                "line": 2,
                "match": {"location": "file2.py:2"},
                "result": {"status": "failed", "duration": 2.0}
            }
        ]
    }
    mock_uuids = ["uuid1", "uuid2"]
    mock_timestamp = "2024-01-01 00:00:00"

    with patch('liveramp_automation.utils.report.uuid.uuid4', side_effect=mock_uuids), \
            patch.dict('liveramp_automation.utils.report.MACROS', {'now_readable': mock_timestamp}):
        # Act
        steps = report_utils_instance._get_steps_from_scenario_(scenario, unique_id)

        # Assert
        for step in steps:
            assert step['step_timestamp'] == mock_timestamp


def test_get_steps_from_scenario_missing_result_key(report_utils_instance):
    """
    Tests _get_steps_from_scenario_ when a step is missing the 'result' key.
    It should raise a KeyError.
    """
    # Arrange
    unique_id = "test-round-uuid-123"
    scenario = {
        "id": "test-scenario-id-456",
        "steps": [
            {
                "name": "Given a user is logged in",
                "keyword": "Given ",
                "line": 10,
                "match": {"location": "features/steps/auth.py:15"},
                # "result": {"status": "passed", "duration": 100.5}  # Missing 'result' key
            }
        ]
    }

    # Act & Assert
    with pytest.raises(KeyError):
        report_utils_instance._get_steps_from_scenario_(scenario, unique_id)


def test_get_steps_from_scenario_missing_duration_field(report_utils_instance):
    """
    Tests _get_steps_from_scenario_ when a step is missing the 'result']['duration'] field.
    It should raise a KeyError.
    """
    # Arrange
    unique_id = "test-round-uuid-123"
    scenario = {
        "id": "test-scenario-id-456",
        "steps": [
            {
                "name": "Given a user is logged in",
                "keyword": "Given ",
                "line": 10,
                "match": {"location": "features/steps/auth.py:15"},
                "result": {"status": "passed"}  # Missing 'duration' field
            }
        ]
    }

    # Act & Assert
    with pytest.raises(KeyError):
        report_utils_instance._get_steps_from_scenario_(scenario, unique_id)


def test_get_steps_from_scenario_missing_match_key(report_utils_instance):
    """
    Tests that _get_steps_from_scenario_ raises a KeyError when a step is missing the 'match' key.
    """
    # Arrange
    unique_id = "test-round-uuid-123"
    scenario = {
        "id": "test-scenario-id-456",
        "steps": [
            {
                "name": "Given a user is logged in",
                "keyword": "Given ",
                "line": 10,
                "result": {"status": "passed", "duration": 100.5}
            }
        ]
    }

    # Act & Assert
    with pytest.raises(KeyError):
        report_utils_instance._get_steps_from_scenario_(scenario, unique_id)


def test_get_steps_from_scenario_missing_match_location_key(report_utils_instance):
    """
    Tests that _get_steps_from_scenario_ raises a KeyError when a step is missing the 'match location' key.
    """
    # Arrange
    unique_id = "test-round-uuid-123"
    scenario = {
        "id": "test-scenario-id-456",
        "steps": [
            {
                "name": "Given a user is logged in",
                "keyword": "Given ",
                "line": 10,
                "match": {},
                "result": {"status": "passed", "duration": 100.5}
            }
        ]
    }

    # Act & Assert
    with pytest.raises(KeyError):
        report_utils_instance._get_steps_from_scenario_(scenario, unique_id)


def test_get_steps_from_scenario_missing_id(report_utils_instance):
    """
    Tests that _get_steps_from_scenario_ raises a KeyError when the scenario
    dictionary does not have an 'id' key.
    """
    # Arrange
    unique_id = "test-round-uuid-123"
    scenario = {
        "steps": [
            {
                "name": "Given a user is logged in",
                "keyword": "Given ",
                "line": 10,
                "match": {"location": "features/steps/auth.py:15"},
                "result": {"status": "passed", "duration": 100.5}
            }
        ]
    }

    # Act & Assert
    with pytest.raises(KeyError):
        report_utils_instance._get_steps_from_scenario_(scenario, unique_id)


def test_get_steps_from_scenario_missing_name_key(report_utils_instance):
    """
    Tests that _get_steps_from_scenario_ raises a KeyError when a step is missing the 'name' key.
    """
    # Arrange
    unique_id = "test-round-uuid-123"
    scenario = {
        "id": "test-scenario-id-456",
        "steps": [
            {
                "keyword": "Given ",
                "line": 10,
                "match": {"location": "features/steps/auth.py:15"},
                "result": {"status": "passed", "duration": 100.5}
            }
        ]
    }

    # Act & Assert
    with pytest.raises(KeyError):
        report_utils_instance._get_steps_from_scenario_(scenario, unique_id)


def test_get_steps_from_scenario_missing_keyword(report_utils_instance):
    """
    Tests that _get_steps_from_scenario_ raises a KeyError when a step is missing the 'keyword' key.
    """
    # Arrange
    unique_id = "test-round-uuid-123"
    scenario = {
        "id": "test-scenario-id-456",
        "steps": [
            {
                "name": "Given a user is logged in",
                "line": 10,
                "match": {"location": "features/steps/auth.py:15"},
                "result": {"status": "passed", "duration": 100.5}
            }
        ]
    }

    # Act & Assert
    with pytest.raises(KeyError):
        report_utils_instance._get_steps_from_scenario_(scenario, unique_id)