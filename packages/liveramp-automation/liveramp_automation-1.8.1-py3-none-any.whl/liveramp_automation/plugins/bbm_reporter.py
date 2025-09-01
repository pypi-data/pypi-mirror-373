"""
BBMReporter is a pytest plugin designed to handle the reporting of test execution data
to BigQuery tables. It collects and organizes test results, including round, feature,
scenario, and step-level details, and formats them into structured data for insertion
into BigQuery. The plugin supports custom configuration through pytest command-line
options, allowing users to specify BigQuery project, dataset, and table names.
Key Features:
- Collects detailed test execution data, including timestamps, statuses, and descriptions.
- Supports custom configuration via pytest command-line options.
- Formats test data into structured rows for BigQuery insertion.
- Handles reporting for individual test calls, including pass, fail, and skip statuses.
"""

import os
import uuid

import pytest
from google.cloud import bigquery

from liveramp_automation.helpers.bucket import BucketHelper
from liveramp_automation.utils.log import Logger
from liveramp_automation.utils.time import MACROS


class BBMReporter:
    """
    BBM Reporter class to handle the reporting of BBM data.
    """

    def __init__(self, config: pytest.Config):
        """
        Initialize the BBMReporter with the given configuration.

        Args:
            config (dict): Configuration dictionary containing necessary parameters.
        """
        self.config: pytest.Config = config
        self.project_id: str = config.getoption("--bbm-bigquery-project-id")
        self.dataset_id: str = config.getoption("--bbm-bigquery-dataset-id")
        self.round_table: str = config.getoption("--bbm-bigquery-round-table")
        self.feature_table: str = config.getoption("--bbm-bigquery-feature-table")
        self.scenario_table: str = config.getoption("--bbm-bigquery-scenario-table")
        self.step_table: str = config.getoption("--bbm-bigquery-step-table")
        self.env: str = config.getoption("--bbm-test-env")
        self.product_name: str = config.getoption("--bbm-test-product")
        self.feature_map: dict = {}
        self.scenario_rows: list = []
        self.step_rows: list = []

        self.round_table_ref: str = (
            f"{self.project_id}.{self.dataset_id}.{self.round_table}"
        )
        self.feature_table_ref: str = (
            f"{self.project_id}.{self.dataset_id}.{self.feature_table}"
        )
        self.scenario_table_ref: str = (
            f"{self.project_id}.{self.dataset_id}.{self.scenario_table}"
        )
        self.step_table_ref: str = (
            f"{self.project_id}.{self.dataset_id}.{self.step_table}"
        )
        self.reporter = None
        self.unique_id = str(uuid.uuid4())

    def insert_into_bigquery(self, rows: list, table_name: str):
        """
        Insert the given rows into the specified BigQuery table.

        Args:
            rows (list): List of dictionaries representing the rows to insert.
            table_name (str): The BigQuery table reference in the format 'project.dataset.table'.
        """

        client = bigquery.Client()
        table_ref = client.get_table(table_name)
        errors = client.insert_rows(table=table_ref, rows=rows)
        if errors:
            Logger.error(
                f"Failed to insert rows into BigQuery table {table_name}: {errors}"
            )

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """
        Pytest hook to process and report test results after each test call.

        Args:
            item (pytest.Item): The test item object.
            call (CallInfo): The call information for the test phase.
        """
        outcome = yield
        if call.when != "call":
            return

        report = outcome.get_result()

        # Ensure the report has scenario information
        if not hasattr(report, "scenario") or not report.scenario:
            Logger.debug(
                f"Skipping report for item '{item.name}' as it has no scenario information."
            )
            return

        scenario = report.scenario
        scenario_id = str(uuid.uuid4())

        # Extract steps from the scenario
        steps = scenario.get("steps", [])
        if not steps:
            Logger.debug(f"Skipping report for item '{item.name}' as it has no steps.")
            return

        # Build step rows and count failures
        scenario_steps = self._build_step_rows(steps, report)
        self.step_rows.extend(scenario_steps)

        # Build scenario row and add step IDs
        scenario_row = self._build_scenario_row(
            scenario=scenario, scenario_id=scenario_id, test_name=item.name
        )
        step_ids = [step["id"] for step in scenario_steps]
        scenario_row["scenario_steps"] = ",".join(step_ids)
        self.scenario_rows.append(scenario_row)

        # Extract feature information and build feature row
        feature = scenario.get("feature", {})
        if not feature:
            Logger.debug(
                f"Skipping report for item '{item.name}' as it has no feature information."
            )
            return

        self._build_feature_row(feature=feature, scenario_id=scenario_id, item=item)

    def _build_feature_row(self, feature: dict, item: pytest.Item, scenario_id: str):
        """
        Build or update a feature row for BigQuery insertion.

        This method checks if the feature (identified by a unique key) has already been processed.
        If not, it creates a new feature row and adds it to the feature_map.
        It also appends the scenario_id to the feature's scenario list.

        Args:
            feature (dict): The feature information dictionary.
            item (pytest.Item, optional): The pytest item object for the test.
            scenario_id (str, optional): The unique ID of the scenario associated with this feature.

        Returns:
            None
        """
        # Construct a unique key for the feature using parent name and feature file name
        parent_name = (
            item.parent.name.split(".")[0] if item and item.parent else "unknown"
        )
        feature_file_name = os.path.basename(feature.get("rel_filename", ""))
        key = f"{parent_name}_{feature_file_name}"

        # Check if the feature has already been processed
        if key in self.feature_map:
            feature_row = self.feature_map[key]
        else:
            feature_row = {
                "id": str(uuid.uuid4()),
                "feature_round_id": self.unique_id,
                "feature_id": feature.get("rel_filename", ""),
                "feature_uri": feature.get("rel_filename", ""),
                "feature_name": feature.get("name", ""),
                "feature_description": feature.get("description", ""),
                "feature_line": int(feature.get("line_number", "0")),
                "feature_keyword": feature.get("keyword", ""),
                "feature_timestamp": MACROS["now_readable"],
                "feature_scenarios": [],
            }
            self.feature_map[key] = feature_row

        # Append the scenario_id to the feature's scenario list if provided
        feature_row["feature_scenarios"].append(scenario_id)

    def _build_scenario_row(
        self, scenario: dict, scenario_id: str, test_name: str
    ) -> dict:
        """
        Build a scenario row dictionary for BigQuery insertion.

        Args:
            scenario (dict): The scenario information dictionary.
            scenario_id (str): The unique ID for the scenario.
            test_name (str): The name of the test item.

        Returns:
            dict: A dictionary representing the scenario row.
        """
        # Extract tags and join them as a comma-separated string
        tags = scenario.get("tags", [])
        tags_str = ",".join(tags) if tags else ""

        scenario_row = {
            "id": scenario_id,
            "scenario_round_id": self.unique_id,
            "scenario_id": test_name,
            "scenario_name": scenario.get("name", ""),
            "scenario_description": scenario.get("description", ""),
            "scenario_line": int(scenario.get("line_number", "0")),
            "scenario_keyword": scenario.get("keyword", ""),
            "scenario_timestamp": MACROS["now_readable"],
            "scenario_tags": tags_str,
        }
        return scenario_row

    def _build_step_rows(self, steps: list, report: pytest.TestReport) -> list:
        """
        Build a list of step row dictionaries for BigQuery insertion.

        Each step in the scenario is processed to create a row with relevant details.
        Only the first failed step (if any) will have the error message attached.

        Args:
            steps (list): List of step dictionaries from the scenario.
            report (pytest.TestReport): The pytest report object for the test.

        Returns:
            list: A list of dictionaries representing step rows.
        """
        scenario_steps = []
        error_attached = False  # Track if error message has been attached

        for step in steps:
            failed = step.get("failed", False)
            step_status = "failed" if failed else "passed"
            # Attach error message only to the first failed step
            error_message = ""
            if failed and not error_attached:
                error_message = getattr(report, "longreprtext", "")
                error_attached = True

            step_row = {
                "id": str(uuid.uuid4()),
                "step_round_id": self.unique_id,
                "step_name": step.get("name", ""),
                "step_keyword": step.get("keyword", ""),
                "step_line": int(step.get("line_number", 0)),
                "step_status": step_status,
                "step_duration": int(step.get("duration", 0)),
                "step_location": step.get("location", ""),
                "step_timestamp": MACROS["now_readable"],
                "step_error_message": error_message,
            }
            scenario_steps.append(step_row)

        return scenario_steps

    def _build_round_row(
        self, features, scenarios, failed_count, round_execution_result
    ):
        """
        Build a round row dictionary for BigQuery insertion.

        This method aggregates the results of the test session, including feature IDs,
        scenario count, and failed step count, and formats them into a dictionary
        suitable for BigQuery insertion.

        Args:
            features (list): List of feature row dictionaries.
            scenarios (list): List of scenario row dictionaries.
            failed_count (int): Number of failed steps or scenarios.
            round_execution_result (str): The overall execution result ("passed" or "failed").

        Returns:
            dict: A dictionary representing the round row.
        """
        # Collect feature IDs as a comma-separated string
        feature_ids = ",".join(f["id"] for f in features)

        round_row = {
            "id": self.unique_id,
            "round_id": self.unique_id,
            "round_execution_env": self.env.upper() if self.env else "",
            "round_suite_name": self.product_name.upper() if self.product_name else "",
            "round_execution_time": MACROS["now"],
            "round_timestamp": MACROS["now_readable"],
            "round_feature_ids": feature_ids,
            "round_execution_result": round_execution_result,
            "round_scenario_count": len(scenarios),
            "round_step_failed_count": failed_count,
        }

        Logger.debug(f"Round row built: {round_row}")
        return round_row

    def update_features_with_scenario_ids(self):
        """
        Prepare feature rows for BigQuery by formatting scenario IDs as a comma-separated string.

        Returns:
            list: List of feature row dictionaries.
        """
        feature_rows = []
        for feature in self.feature_map.values():
            # Join scenario IDs into a comma-separated string for BigQuery compatibility
            feature["feature_scenarios"] = ",".join(
                feature.get("feature_scenarios", [])
            )
            feature_rows.append(feature)
        return feature_rows

    def upload_artifacts_to_gcs_bucket(self):
        """
        Upload test artifacts from the local report folder to a specified Google Cloud Storage (GCS) bucket.

        This method retrieves the bucket name, report folder, and destination path from the pytest configuration,
        then uploads the contents of the report folder to the GCS bucket at the specified path using BucketHelper.

        Returns:
            None
        """
        bucket_name = self.config.getoption("--bbm-bucket-name")
        report_folder = self.config.getoption("--bbm-report-folder")
        path_name = self.config.getoption("--bbm-bucket-path-name")

        Logger.debug(
            f"Uploading artifacts from '{report_folder}' to GCS bucket '{bucket_name}' at path '{path_name}'."
        )

        # Initialize the BucketHelper and upload the report folder to the specified GCS path
        bucket_helper = BucketHelper(self.project_id, bucket_name)
        bucket_helper.upload_file(report_folder, path_name)

    def pytest_sessionfinish(self, session: pytest.Session):
        """
        Pytest hook to handle the end of the test session and report results to BigQuery.

        This method is called after the entire test session finishes. It aggregates
        all collected feature, scenario, and step data, builds the round summary,
        and inserts all rows into their respective BigQuery tables.

        Args:
            session (pytest.Session): The pytest session object containing test results.
        """

        # Determine overall execution result based on failed tests
        round_execution_result = "failed" if session.testsfailed > 0 else "passed"
        Logger.debug(
            f"Session finished with result: {round_execution_result} (tests failed: {session.testsfailed})"
        )

        # Gather all feature rows for reporting
        feature_rows = self.update_features_with_scenario_ids()
        Logger.debug(f"Collected {len(feature_rows)} feature rows for reporting.")

        # Build the round summary row
        test_round = self._build_round_row(
            features=feature_rows,
            scenarios=self.scenario_rows,
            failed_count=session.testsfailed,
            round_execution_result=round_execution_result,
        )
        Logger.debug("Inserting feature, scenario, step, and round data into BigQuery.")
        # Insert feature, scenario, step, and round data into BigQuery
        self.insert_into_bigquery(rows=feature_rows, table_name=self.feature_table_ref)

        self.insert_into_bigquery(
            rows=self.scenario_rows, table_name=self.scenario_table_ref
        )

        self.insert_into_bigquery(rows=self.step_rows, table_name=self.step_table_ref)

        self.insert_into_bigquery(rows=[test_round], table_name=self.round_table_ref)
        Logger.debug("Completed all BigQuery insertions.")

        # Upload test artifacts to GCS bucket
        self.upload_artifacts_to_gcs_bucket()


def pytest_addoption(parser: pytest.Parser):
    """
    Pytest hook to add custom command line options.

    Args:
        parser (pytest.Parser): The pytest parser object.
    """
    group = parser.getgroup("BBM Reporter")
    group.addoption(
        "--bbm-reporter",
        action="store_true",
        default=False,
        help="Enable the BBM Reporter plugin to handle BBM data reporting. Default: False",
    )
    group.addoption(
        "--bbm-bigquery-project-id",
        action="store",
        default="liveramp-eng-qa-reliability",
        help="Specify the BigQuery project ID to use for BBM reporting. Default: 'liveramp-eng-qa-reliability'",
    )
    group.addoption(
        "--bbm-bigquery-dataset-id",
        action="store",
        default="customer_impact_hours",
        help="Specify the BigQuery dataset ID to use for BBM reporting. Default: 'customer_impact_hours'",
    )
    group.addoption(
        "--bbm-bigquery-round-table",
        action="store",
        default="bbm_round_table",
        help="Specify the BigQuery table name for storing round data. Default: 'bbm_round_table'",
    )
    group.addoption(
        "--bbm-bigquery-feature-table",
        action="store",
        default="bbm_feature_table",
        help="Specify the BigQuery table name for storing feature data. Default: 'bbm_feature_table'",
    )
    group.addoption(
        "--bbm-bigquery-scenario-table",
        action="store",
        default="bbm_scenario_table",
        help="Specify the BigQuery table name for storing scenario data. Default: 'bbm_scenario_table'",
    )
    group.addoption(
        "--bbm-bigquery-step-table",
        action="store",
        default="bbm_step_table",
        help="Specify the BigQuery table name for storing step data. Default: 'bbm_step_table'",
    )
    group.addoption(
        "--bbm-test-env",
        action="store",
        default=os.getenv(key="ENVCHOICE", default="PROD").upper(),
        help="Specify the test environment for BBM reporting. Default: 'prod'",
    )
    group.addoption(
        "--bbm-test-product",
        action="store",
        default=os.getenv(key="PRODUCTNAME", default="").upper(),
        help="Specify the product name for BBM reporting. Default(Empty): ''",
    )
    group.addoption(
        "--bbm-bucket-name",
        action="store",
        default=os.getenv(key="BUCKET_NAME", default="bbm-e2e-tests"),
        help="Specify the Google Cloud Storage bucket name for uploading test artifacts. Default: value of BUCKET_NAME env var or 'bbm-e2e-tests'.",
    )
    group.addoption(
        "--bbm-bucket-path-name",
        action="store",
        default=os.getenv(key="BUCKET_PATH_NAME", default="default_bucket"),
        help="Specify the destination path in the GCS bucket for test artifacts. Default: value of BUCKET_PATH_NAME env var or 'default_bucket'.",
    )
    group.addoption(
        "--bbm-report-folder",
        action="store",
        default="reports",
        help="Specify the local folder containing test artifacts to upload. Default: 'reports'.",
    )


def pytest_configure(config: pytest.Config):
    """
    Pytest configuration hook to add custom command line options.

    Args:
        config (pytest.Config): The pytest configuration object.
    """
    if config.getoption("--bbm-reporter"):
        config.pluginmanager.register(BBMReporter(config))
