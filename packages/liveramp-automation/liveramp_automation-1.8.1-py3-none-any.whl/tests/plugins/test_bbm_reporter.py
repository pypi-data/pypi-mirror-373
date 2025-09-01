import pytest
from unittest.mock import MagicMock, patch
from liveramp_automation.plugins.bbm_reporter import BBMReporter
from liveramp_automation.utils.time import MACROS


@pytest.fixture
def mock_config():
    config = MagicMock()
    config.getoption.side_effect = lambda opt: (
        "test_project"
        if opt == "--bbm-bigquery-project-id"
        else "test_dataset"
        if opt == "--bbm-bigquery-dataset-id"
        else "round_table"
        if opt == "--bbm-bigquery-round-table"
        else "feature_table"
        if opt == "--bbm-bigquery-feature-table"
        else "scenario_table"
        if opt == "--bbm-bigquery-scenario-table"
        else "step_table"
        if opt == "--bbm-bigquery-step-table"
        else "test_env"
        if opt == "--bbm-test-env"
        else "test_product"
        if opt == "--bbm-test-product"
        else "test_bucket"
        if opt == "--bbm-bucket-name"
        else "test_reports"
        if opt == "--bbm-report-folder"
        else "test_path"
        if opt == "--bbm-bucket-path-name"
        else None
    )
    return config


@pytest.fixture
def reporter(mock_config):
    bbm = BBMReporter(mock_config)
    bbm.env = "test_env"
    bbm.product = "test_product"
    return bbm


def test_insert_into_bigquery_success(reporter):
    with patch("liveramp_automation.plugins.bbm_reporter.bigquery.Client") as mock_client:
        mock_instance = mock_client.return_value
        mock_instance.get_table.return_value = "table_ref"
        mock_instance.insert_rows.return_value = []
        reporter.insert_into_bigquery([{"foo": "bar"}], "table_name")
        mock_instance.insert_rows.assert_called_once()


def test_insert_into_bigquery_failure(reporter):
    with patch("liveramp_automation.plugins.bbm_reporter.bigquery.Client") as mock_client, \
            patch("liveramp_automation.plugins.bbm_reporter.Logger") as mock_logger:
        mock_instance = mock_client.return_value
        mock_instance.get_table.return_value = "table_ref"
        mock_instance.insert_rows.return_value = ["error"]
        reporter.insert_into_bigquery([{"foo": "bar"}], "table_name")
        mock_logger.error.assert_called_once()


def test_build_scenario_row(reporter):
    scenario = {
        "name": "Scenario 1",
        "description": "desc",
        "line_number": 10,
        "keyword": "Scenario",
        "tags": ["tag1", "tag2"]
    }
    row = reporter._build_scenario_row(scenario, "sid", "test_name")
    assert row["scenario_name"] == "Scenario 1"
    assert row["scenario_tags"] == "tag1,tag2"


def test_build_scenario_row_all_fields(reporter):
    scenario = {
        "name": "Scenario Name",
        "description": "Scenario Description",
        "line_number": 123,
        "keyword": "Scenario Keyword",
        "tags": ["tag1", "tag2"]
    }
    scenario_id = "test_scenario_id"
    test_name = "test_test_name"
    expected_tags = "tag1,tag2"
    row = reporter._build_scenario_row(scenario, scenario_id, test_name)
    assert row["id"] == scenario_id
    assert row["scenario_round_id"] == reporter.unique_id
    assert row["scenario_id"] == test_name
    assert row["scenario_name"] == "Scenario Name"
    assert row["scenario_description"] == "Scenario Description"
    assert row["scenario_line"] == 123
    assert row["scenario_keyword"] == "Scenario Keyword"
    assert row["scenario_tags"] == expected_tags
    assert row["scenario_timestamp"] == MACROS["now_readable"]


def test_build_scenario_row_defaults(reporter):
    scenario = {
        "name": "Scenario 1",
    }
    row = reporter._build_scenario_row(scenario, "sid", "test_name")
    assert row["scenario_name"] == "Scenario 1"
    assert row["scenario_description"] == ""
    assert row["scenario_keyword"] == ""
    assert row["scenario_tags"] == ""
    assert row["scenario_line"] == 0


def test_build_scenario_row_none_tags(reporter):
    scenario = {
        "name": "Scenario with None tags",
        "description": "desc",
        "line_number": 10,
        "keyword": "Scenario",
        "tags": None
    }
    row = reporter._build_scenario_row(scenario, "sid", "test_name")
    assert row["scenario_tags"] == ""


def test_build_scenario_row_empty_strings(reporter):
    scenario = {
        "name": "Scenario 1",
        "description": "desc",
        "line_number": 10,
        "keyword": "Scenario",
        "tags": ["tag1", "tag2"]
    }
    row = reporter._build_scenario_row(scenario, "", "")
    assert row["id"] == ""
    assert row["scenario_id"] == ""


def test_build_step_rows(reporter):
    steps = [
        {"name": "step1", "keyword": "Given", "line_number": 1, "duration": 1, "location": "loc1"},
        {"name": "step2", "keyword": "When", "line_number": 2, "duration": 2, "location": "loc2", "failed": True}
    ]
    report = MagicMock()
    report.longreprtext = "error details"
    rows = reporter._build_step_rows(steps, report)
    assert len(rows) == 2
    assert rows[1]["step_status"] == "failed"
    assert rows[1]["step_error_message"] == "error details"


def test_build_step_rows_multiple_failures(reporter):
    steps = [
        {"name": "step1", "keyword": "Given", "line_number": 1, "duration": 1, "location": "loc1", "failed": True},
        {"name": "step2", "keyword": "When", "line_number": 2, "duration": 2, "location": "loc2"},
        {"name": "step3", "keyword": "Then", "line_number": 3, "duration": 3, "location": "loc3", "failed": True}
    ]
    report = MagicMock()
    report.longreprtext = "error details"
    rows = reporter._build_step_rows(steps, report)
    assert len(rows) == 3
    assert rows[0]["step_status"] == "failed"
    assert rows[0]["step_error_message"] == "error details"
    assert rows[2]["step_status"] == "failed"
    assert rows[2]["step_error_message"] == ""


def test_build_step_rows_missing_optional_fields(reporter):
    steps = [
        {},
        {"failed": True},
        {"name": "step1"},
        {"keyword": "Given"},
        {"line_number": 1},
        {"duration": 1},
        {"location": "loc1"},
    ]
    report = MagicMock()
    report.longreprtext = "error details"
    rows = reporter._build_step_rows(steps, report)
    assert len(rows) == 7

    # Check default values for the first step
    assert rows[0]["step_name"] == ""
    assert rows[0]["step_keyword"] == ""
    assert rows[0]["step_line"] == 0
    assert rows[0]["step_status"] == "passed"
    assert rows[0]["step_duration"] == 0
    assert rows[0]["step_location"] == ""

    # Check default values and failed status for the second step
    assert rows[1]["step_status"] == "failed"

    # Check that the existing values are preserved for the other steps
    assert rows[2]["step_name"] == "step1"
    assert rows[3]["step_keyword"] == "Given"
    assert rows[4]["step_line"] == 1
    assert rows[5]["step_duration"] == 1
    assert rows[6]["step_location"] == "loc1"


def test_build_step_rows_invalid_line_number(reporter):
    steps = [
        {"name": "step1", "keyword": "Given", "line_number": "abc", "duration": 1, "location": "loc1"},
    ]
    report = MagicMock()
    with pytest.raises(ValueError):
        reporter._build_step_rows(steps, report)


def test_build_step_rows_invalid_duration(reporter):
    steps = [
        {"name": "step1", "keyword": "Given", "line_number": 1, "duration": "invalid", "location": "loc1"}
    ]
    report = MagicMock()
    with pytest.raises(ValueError):
        reporter._build_step_rows(steps, report)


def test_build_step_rows_non_dict_step(reporter):
    steps = [
        {"name": "step1", "keyword": "Given", "line_number": 1, "duration": 1, "location": "loc1"},
        "not a dict",
        {"name": "step2", "keyword": "When", "line_number": 2, "duration": 2, "location": "loc2", "failed": True}
    ]
    report = MagicMock()
    report.longreprtext = "error details"
    with pytest.raises(AttributeError):
        reporter._build_step_rows(steps, report)


def test_build_step_rows_missing_longreprtext(reporter):
    steps = [
        {"name": "step1", "keyword": "Given", "line_number": 1, "duration": 1, "location": "loc1", "failed": True}
    ]

    class ReportWithoutLongreprtext:
        pass

    report = ReportWithoutLongreprtext()

    rows = reporter._build_step_rows(steps, report)
    assert len(rows) == 1
    assert rows[0]["step_status"] == "failed"
    assert rows[0]["step_error_message"] == ""


def test_build_step_rows_empty_steps(reporter):
    report = MagicMock()
    steps = []
    rows = reporter._build_step_rows(steps, report)
    assert rows == []


def test_build_feature_row_new_and_existing(reporter):
    feature = {"rel_filename": "file.feature",
               "name": "Feature", "description":
                   "desc", "line_number": 5,
               "keyword": "Feature"}
    item = MagicMock()
    item.parent.name = "parent.py"
    scenario_id = "sid"
    reporter._build_feature_row(feature, item, scenario_id)
    assert len(reporter.feature_map) == 1
    # Call again to test existing feature
    reporter._build_feature_row(feature, item, "sid2")
    key = "parent_file.feature"
    assert len(reporter.feature_map[key]["feature_scenarios"]) == 2


def test_build_feature_row_empty_rel_filename(reporter):
    feature = {"rel_filename": "",
               "name": "Feature", "description": "desc",
               "line_number": 5, "keyword": "Feature"}
    item = MagicMock()
    item.parent.name = "parent.py"
    scenario_id = "sid"
    reporter._build_feature_row(feature, item, scenario_id)
    key = "parent_"
    assert key in reporter.feature_map
    assert reporter.feature_map[key]["feature_name"] == "Feature"
    assert reporter.feature_map[key]["feature_id"] == ""


def test_build_feature_row_empty_scenario_id(reporter):
    feature = {"rel_filename": "file.feature", "name": "Feature", "description": "desc", "line_number": 5, "keyword": "Feature"}
    item = MagicMock()
    item.parent.name = "parent.py"

    # Test with None scenario_id
    reporter._build_feature_row(feature, item, None)
    key = "parent_file.feature"
    assert len(reporter.feature_map) == 1
    assert reporter.feature_map[key]["feature_scenarios"] == [None]
    reporter.feature_map = {}

    # Test with empty string scenario_id
    reporter._build_feature_row(feature, item, "")
    assert len(reporter.feature_map) == 1
    assert reporter.feature_map["parent_file.feature"]["feature_scenarios"] == [""]


def test_build_feature_row_no_parent_name(reporter):
    """
    Tests the scenario where item.parent is None or doesn't have a name attribute.
    """
    feature = {"rel_filename": "file.feature", "name": "Feature", "description": "desc", "line_number": 5,
               "keyword": "Feature"}
    item = MagicMock()
    item.parent = None
    scenario_id = "sid"
    reporter._build_feature_row(feature, item, scenario_id)
    key = "unknown_file.feature"
    assert key in reporter.feature_map


def test_update_features_with_scenario_ids(reporter):
    reporter.feature_map = {
        "k1": {"feature_scenarios": ["s1", "s2"], "id": "id1"},
        "k2": {"feature_scenarios": ["s3"], "id": "id2"},
    }
    rows = reporter.update_features_with_scenario_ids()
    assert rows[0]["feature_scenarios"] == "s1,s2"
    assert rows[1]["feature_scenarios"] == "s3"


def test_build_round_row(reporter):
    features = [{"id": "f1"}, {"id": "f2"}]
    scenarios = [1, 2, 3]
    row = reporter._build_round_row(features, scenarios, 1, "passed")
    assert row["round_feature_ids"] == "f1,f2"
    assert row["round_scenario_count"] == 3
    assert row["round_execution_result"] == "passed"


def test_build_round_row_empty_features(reporter):
    features = []
    scenarios = [1, 2, 3]
    row = reporter._build_round_row(features, scenarios, 1, "passed")
    assert row["round_feature_ids"] == ""
    assert row["round_scenario_count"] == 3
    assert row["round_execution_result"] == "passed"


def test_upload_artifacts_to_gcs_bucket(reporter):
    with patch("liveramp_automation.plugins.bbm_reporter.BucketHelper") as mock_helper:
        instance = mock_helper.return_value
        reporter.upload_artifacts_to_gcs_bucket()
        instance.upload_file.assert_called_once()


def test_pytest_sessionfinish(reporter):
    with patch.object(reporter, "update_features_with_scenario_ids",
                      return_value=[{"id": "f1", "feature_scenarios": "s1"}]), \
            patch.object(reporter, "insert_into_bigquery") as mock_insert, \
            patch.object(reporter, "upload_artifacts_to_gcs_bucket") as mock_upload:
        reporter.scenario_rows = [{"id": "s1"}]
        reporter.step_rows = [{"id": "step1"}]
        session = MagicMock()
        session.testsfailed = 0
        reporter.pytest_sessionfinish(session)
        assert mock_insert.call_count == 4
        mock_upload.assert_called_once()


def test_pytest_runtest_makereport_happy_path(reporter):
    """
    Tests the happy path for pytest_runtest_makereport where a report in the 'call'
    phase contains valid scenario, steps, and feature information.
    """
    # Arrange: Set up mock pytest objects and report data.
    item = MagicMock()
    item.name = "test_scenario_name"
    item.parent.name = "test_parent.py"

    call = MagicMock()
    call.when = "call"

    report = MagicMock()
    report.scenario = {
        "name": "Test Scenario",
        "description": "A test scenario description.",
        "line_number": 5,
        "keyword": "Scenario",
        "tags": ["happy_path", "smoke"],
        "steps": [
            {
                "name": "a passing step",
                "keyword": "Given",
                "line_number": 6,
                "duration": 1.0,
                "location": "loc1",
                "failed": False,
            },
            {
                "name": "another passing step",
                "keyword": "When",
                "line_number": 7,
                "duration": 2.0,
                "location": "loc2",
                "failed": False,
            },
        ],
        "feature": {
            "rel_filename": "path/to/my_feature.feature",
            "name": "Test Feature",
            "description": "A test feature description.",
            "line_number": 1,
            "keyword": "Feature",
        },
    }
    report.longreprtext = ""  # No error for passing steps

    outcome = MagicMock()
    outcome.get_result.return_value = report

    # Define predictable UUIDs to be returned by the mock
    mock_uuid_values = [
        "scenario-uuid-1",  # For the scenario
        "step-uuid-1",      # For the first step
        "step-uuid-2",      # For the second step
        "feature-uuid-1",   # For the new feature
    ]

    with patch(
        "liveramp_automation.plugins.bbm_reporter.uuid.uuid4",
        side_effect=[str(val) for val in mock_uuid_values],
    ):
        # Act: Simulate the hookwrapper call.
        gen = reporter.pytest_runtest_makereport(item, call)
        next(gen)  # Execute up to the 'yield'
        try:
            gen.send(outcome)  # Resume execution after 'yield' with the mock outcome
        except StopIteration:
            pass  # StopIteration is expected when a generator finishes

        # Assert: Verify that the reporter's state was updated correctly.
        # Check step_rows
        assert len(reporter.step_rows) == 2
        assert reporter.step_rows[0]["id"] == "step-uuid-1"
        assert reporter.step_rows[0]["step_name"] == "a passing step"
        assert reporter.step_rows[0]["step_status"] == "passed"
        assert reporter.step_rows[1]["id"] == "step-uuid-2"
        assert reporter.step_rows[1]["step_name"] == "another passing step"

        # Check scenario_rows
        assert len(reporter.scenario_rows) == 1
        scenario_row = reporter.scenario_rows[0]
        assert scenario_row["id"] == "scenario-uuid-1"
        assert scenario_row["scenario_name"] == "Test Scenario"
        assert scenario_row["scenario_id"] == "test_scenario_name"
        assert scenario_row["scenario_tags"] == "happy_path,smoke"
        assert scenario_row["scenario_steps"] == "step-uuid-1,step-uuid-2"

        # Check feature_map
        assert len(reporter.feature_map) == 1
        feature_key = "test_parent_my_feature.feature"
        assert feature_key in reporter.feature_map
        feature_row = reporter.feature_map[feature_key]
        assert feature_row["id"] == "feature-uuid-1"
        assert feature_row["feature_name"] == "Test Feature"
        assert feature_row["feature_scenarios"] == ["scenario-uuid-1"]


def test_pytest_runtest_makereport_exception_handling(reporter):
    """
    Tests that pytest_runtest_makereport handles exceptions raised during report processing,
    specifically within the _build_step_rows method.
    """
    # Arrange: Mock _build_step_rows to raise an exception.
    with patch.object(reporter, "_build_step_rows", side_effect=ValueError("Malformed step data")):
        item = MagicMock()
        item.name = "test_scenario_name"

        call = MagicMock()
        call.when = "call"

        report = MagicMock()
        report.scenario = {
            "name": "Test Scenario",
            "description": "A test scenario description.",
            "line_number": 5,
            "keyword": "Scenario",
            "tags": ["exception_test"],
            "steps": [
                {
                    "name": "a passing step",
                    "keyword": "Given",
                    "line_number": 6,
                    "duration": 1.0,
                    "location": "loc1",
                    "failed": False,
                }
            ],
            "feature": {
                "rel_filename": "path/to/my_feature.feature",
                "name": "Test Feature",
                "description": "A test feature description.",
                "line_number": 1,
                "keyword": "Feature",
            },
        }

        outcome = MagicMock()
        outcome.get_result.return_value = report

        # Act & Assert: Call pytest_runtest_makereport and assert that it handles the exception.
        gen = reporter.pytest_runtest_makereport(item, call)
        next(gen)  # Execute up to the 'yield'
        with pytest.raises(ValueError, match="Malformed step data"):
            gen.send(outcome)  # Resume execution after 'yield' with the mock outcome


def test_pytest_runtest_makereport_early_return(reporter):
    """
    Tests that pytest_runtest_makereport returns early when call.when is not 'call'.
    """
    item = MagicMock()
    call = MagicMock()
    call.when = "setup"  # or "teardown"
    outcome = MagicMock()

    with patch.object(reporter, "_build_step_rows") as mock_build_step_rows, \
            patch.object(reporter, "_build_scenario_row") as mock_build_scenario_row, \
            patch.object(reporter, "_build_feature_row") as mock_build_feature_row, \
            patch("liveramp_automation.plugins.bbm_reporter.Logger") as mock_logger:
        result = reporter.pytest_runtest_makereport(item, call)
        result_list = list(result)
        assert len(result_list) == 1
        assert result_list[0] is None
        mock_build_step_rows.assert_not_called()
        mock_build_scenario_row.assert_not_called()
        mock_build_feature_row.assert_not_called()
        mock_logger.debug.assert_not_called()


def test_pytest_runtest_makereport_no_scenario_info(reporter):
    """
    Tests the scenario where pytest_runtest_makereport is called with a report
    that does not have scenario information.
    """
    item = MagicMock()
    item.name = "test_item_name"

    call = MagicMock()
    call.when = "call"

    report = MagicMock()
    # Report does not have the 'scenario' attribute
    del report.scenario

    outcome = MagicMock()
    outcome.get_result.return_value = report

    with patch("liveramp_automation.plugins.bbm_reporter.Logger") as mock_logger:
        # Act: Simulate the hookwrapper call.
        gen = reporter.pytest_runtest_makereport(item, call)
        next(gen)  # Execute up to the 'yield'
        try:
            gen.send(outcome)  # Resume execution after 'yield' with the mock outcome
        except StopIteration:
            pass  # StopIteration is expected when a generator finishes

        # Assert: Verify that Logger.debug was called and that the function returns early.
        mock_logger.debug.assert_called_once_with(
            f"Skipping report for item '{item.name}' as it has no scenario information."
        )

        # Assert that no scenario rows were added, implying an early return.
        assert len(reporter.scenario_rows) == 0


def test_pytest_runtest_makereport_no_feature_info(reporter):
    """
    Tests the scenario where pytest_runtest_makereport is called with a report
    that has no feature information. It asserts that the function returns early
    and logs a debug message.
    """
    # Arrange: Mock pytest objects and report data with no feature information.
    item = MagicMock()
    item.name = "test_scenario_name"

    call = MagicMock()
    call.when = "call"

    report = MagicMock()
    report.scenario = {
        "name": "Test Scenario",
        "description": "A test scenario description.",
        "line_number": 5,
        "keyword": "Scenario",
        "tags": ["no_feature"],
        "steps": [
            {
                "name": "a passing step",
                "keyword": "Given",
                "line_number": 6,
                "duration": 1.0,
                "location": "loc1",
                "failed": False,
            }
        ],
        # No feature information
    }

    outcome = MagicMock()
    outcome.get_result.return_value = report

    with patch("liveramp_automation.plugins.bbm_reporter.Logger") as mock_logger:
        # Act: Simulate the hookwrapper call.
        gen = reporter.pytest_runtest_makereport(item, call)
        next(gen)  # Execute up to the 'yield'
        try:
            gen.send(outcome)  # Resume execution after 'yield' with the mock outcome
        except StopIteration:
            pass  # StopIteration is expected when a generator finishes

        # Assert: Verify that Logger.debug was called and other methods were not.
        mock_logger.debug.assert_called_once_with(
            f"Skipping report for item '{item.name}' as it has no feature information."
        )
        assert len(reporter.step_rows) == 1
        assert len(reporter.scenario_rows) == 1
        assert len(reporter.feature_map) == 0


def test_pytest_runtest_makereport_steps_none(reporter):
    """
    Tests the scenario where scenario['steps'] is None.
    The code should log a debug message and return.
    """
    item = MagicMock()
    item.name = "test_scenario_name"

    call = MagicMock()
    call.when = "call"

    report = MagicMock()
    report.scenario = {
        "name": "Test Scenario",
        "description": "A test scenario description.",
        "line_number": 5,
        "keyword": "Scenario",
        "tags": ["steps_none", "edge"],
        "steps": None,  # steps is None
        "feature": {
            "rel_filename": "path/to/my_feature.feature",
            "name": "Test Feature",
            "description": "A test feature description.",
            "line_number": 1,
            "keyword": "Feature",
        },
    }
    report.longreprtext = ""

    outcome = MagicMock()
    outcome.get_result.return_value = report

    with patch("liveramp_automation.plugins.bbm_reporter.Logger") as mock_logger:
        # Act
        gen = reporter.pytest_runtest_makereport(item, call)
        next(gen)
        try:
            gen.send(outcome)
        except StopIteration:
            pass

        # Assert
        mock_logger.debug.assert_called_once_with(
            "Skipping report for item 'test_scenario_name' as it has no steps."
        )
        assert len(reporter.step_rows) == 0
        assert len(reporter.scenario_rows) == 0
        assert len(reporter.feature_map) == 0


def test_pytest_runtest_makereport_predetermined_scenario_id(reporter):
    """
    Tests that pytest_runtest_makereport uses a predetermined scenario_id when uuid.uuid4 is mocked.
    """
    # Arrange
    item = MagicMock()
    item.name = "test_scenario_name"
    item.parent.name = "test_parent.py"

    call = MagicMock()
    call.when = "call"

    report = MagicMock()
    report.scenario = {
        "name": "Test Scenario",
        "description": "A test scenario description.",
        "line_number": 5,
        "keyword": "Scenario",
        "tags": ["predetermined_id"],
        "steps": [
            {
                "name": "a test step",
                "keyword": "Given",
                "line_number": 6,
                "status": "passed"
            }
        ],
        "feature": {
            "rel_filename": "path/to/my_feature.feature",
            "name": "Test Feature",
            "description": "A test feature description.",
            "line_number": 1,
            "keyword": "Feature",
        },
    }
    report.longreprtext = ""

    outcome = MagicMock()
    outcome.get_result.return_value = report

    predetermined_uuid = "predetermined-scenario-id"

    with patch("liveramp_automation.plugins.bbm_reporter.uuid.uuid4", return_value=predetermined_uuid):
        # Act
        gen = reporter.pytest_runtest_makereport(item, call)
        next(gen)
        try:
            gen.send(outcome)
        except StopIteration:
            pass

        # Assert
        assert len(reporter.scenario_rows) == 1
        scenario_row = reporter.scenario_rows[0]
        assert scenario_row["id"] == predetermined_uuid