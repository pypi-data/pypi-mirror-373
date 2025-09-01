import base64
import os
from datetime import datetime
from typing import Literal, Optional, List
import pytest
import requests

from liveramp_automation.utils.log import Logger


class TestrailReporter:
    """
    A pytest plugin that integrates with TestRail for reporting test results.

    This plugin automates the creation of test runs in TestRail and associates test results with
    respective test cases using markers in feature files.

    Attributes:
        config (pytest.Config): Pytest configuration object.
        testrail_url (str): Base URL of the TestRail instance.
        user_name (str): Username for TestRail authentication.
        password (str): Password or API key for TestRail authentication.
        project_id (Optional[int]): ID of the TestRail project.
        suite_id (Optional[int]): ID of the TestRail test suite.
        run_id (Optional[int]): ID of the created or existing TestRail test run.
        run_name (Optional[str]): Name of the test run.
        session (requests.Session): HTTP session for API requests.
    """

    def __init__(self, config):
        """
        Initializes the TestRail reporter plugin.

        Args:
            config (pytest.Config): The pytest configuration object.
        """
        self.config = config
        self.testrail_url = None
        self.user_name = None
        self.password = None
        self.project_id = None
        self.suite_id = None
        self.run_id = None
        self.run_name = None
        self.session = requests.session()

    @property
    def headers(self) -> dict:
        """
        Constructs authentication headers for TestRail API requests.

        Returns:
            dict: Headers including Basic Authentication and Content-Type.
        """
        auth = base64.b64encode(
            f"{self.user_name}:{self.password}".encode("utf-8")
        ).decode("ascii")

        return {"Authorization": f"Basic {auth}", "Content-Type": "application/json"}

    def get_project_name(self) -> str:
        """
        Retrieves the project name from TestRail using the project ID.

        Returns:
            str: The project name if found, otherwise an empty string.
        """
        get_project_url = (
            f"{self.testrail_url}/index.php?/api/v2/get_project/{self.project_id}"
        )
        response = self.session.get(get_project_url, headers=self.headers)

        if not response.ok:
            Logger.error(f"Failed to fetch project name from TestRail: {response.text}")
            return ""

        return response.json().get("name", "")

    def get_suite_name(self) -> str:
        """
        Retrieves the test suite name from TestRail using the suite ID.

        Returns:
            str: The suite name if found, otherwise an empty string.
        """
        get_suite_url = (
            f"{self.testrail_url}/index.php?/api/v2/get_suite/{self.suite_id}"
        )
        response = self.session.get(get_suite_url, headers=self.headers)

        if not response.ok:
            Logger.error(f"Failed to fetch suite name from TestRail: {response.text}")
            return ""

        return response.json().get("name", "")

    def add_run(self, case_ids: List) -> Optional[int]:
        """
        Creates a new test run in TestRail.

        Returns:
            Optional[int]: The ID of the created test run if successful, otherwise None.
        """
        Logger.info(
            f"Creating test run with Project ID: {self.project_id}, Suite ID: {self.suite_id}"
        )
        self.session.headers = self.headers

        add_run_url = f"{self.testrail_url}/index.php?/api/v2/add_run/{self.project_id}"
        project_name = self.get_project_name()
        suite_name = self.get_suite_name()

        if not self.run_name:
            timestamp = datetime.now().strftime("%d-%m-%Y-%H-%M")
            self.run_name = f"AutomationReport {project_name} - {suite_name} - {timestamp}"

        payload = {
            "suite_id": self.suite_id,
            "name": self.run_name,
            "description": f"Automated test run for suite {suite_name}",
            "include_all": False,
            "case_ids": case_ids,
        }

        response = self.session.post(
            url=add_run_url, headers=self.headers, json=payload
        )

        if not response.ok:
            Logger.error(f"Error while creating run in TestRail: {response.text}")
            return None

        return response.json().get("id")

    def add_test_case_result_to_run(
        self, case_id: str, status: int, message: str, elapsed_time: float
    ):
        """
        Add the result of a test case to the TestRail run.

        Args:
            case_id (str): The ID of the test case.
            status (int): The status of the test (e.g., 1 for passed, 5 for failed).
            message (str): The result message or error message.
            elapsed_time (float): The time taken to run the test case.
        """
        # Prepare API request to update the test case result
        add_result_url = f"{self.testrail_url}/index.php?/api/v2/add_result_for_case/{self.run_id}/{case_id}"
        payload = {
            "status_id": status,  # 1 for passed, 5 for failed
            "comment": message,
            "elapsed": f"{max(1, int(elapsed_time))}s",  # Format elapsed time to 2 decimal places
        }
        response = self.session.post(
            url=add_result_url, headers=self.headers, json=payload
        )

        if response.ok:
            Logger.info(f"Successfully added result for case {case_id}.")
        else:
            Logger.error(f"Failed to add result for case {case_id}: {response.text}")
        return response

    def get_id_from_marker(
        self,
        item: pytest.Item,
        marker_prefix: Literal["projectid", "suiteid", "caseid"],
    ) -> Optional[str]:
        """
        Extracts an ID from a pytest marker formatted as 'markername:value'.

        Args:
            item (pytest.Item): A pytest test case item.
            marker_prefix (Literal["projectid", "suiteid", "caseid"]): The prefix to search for.

        Returns:
            Optional[str]: The extracted ID if found, otherwise None.
        """
        for marker in item.iter_markers():
            if marker.name.startswith(f"{marker_prefix}:"):
                return marker.name.split(":", 1)[1].strip()

        return None

    def get_scenario_step_wise_status(self, scenario_data: dict):
        """
        Getting scenario step-wise status
        Args:
            scenario_data (dict): The scenario data dictionary.

        Returns:
            str: Formatted scenario report.
        """

        # Feature Information
        feature = scenario_data.get("feature", {})
        output = [
            f"Feature: {feature.get('name', 'Unknown')} ({feature.get('filename', 'N/A')})"
        ]

        if feature.get("description"):
            output.append(f"\tDescription: {feature.get('description', '')}")

        output.append("")  # Blank line for readability

        # Scenario Information
        output.append(f"\tScenario: {scenario_data.get('name', 'Unknown')}")

        if scenario_data.get("description"):
            output.append(f"\t\tDescription: {scenario_data.get('description', '')}")

        # Rule Information (if present)
        rule = scenario_data.get("rule", {})
        if rule:
            output.append(f"\t\tRule: {rule.get('name', 'Unnamed Rule')}")
            if rule.get("description"):
                output.append(f"\t\t\tDescription: {rule.get('description', '')}")
            output.append("")  # Blank line for readability

        # Steps Information
        output.append("\t\tSteps:")
        for step in scenario_data.get("steps", []):
            status = "PASSED" if not step.get("failed", False) else "FAILED"
            step_info = f"\t\t\t{step.get('keyword', 'UNKNOWN')} {step.get('name', 'Unnamed Step')} - {status}"
            output.append(step_info)

            # Include error message if step failed
            if step.get("failed") and step.get("error_message"):
                output.append(
                    f"\t\t\t\tError: {step.get('error_message', 'Unknown error')}"
                )

        return "\n".join(output)

    @pytest.hookimpl(trylast=True)
    def pytest_collection_finish(self, session):
        """
        Hook executed after test collection and before execution.

        1. Checks if the user provided project_id and suite_id via command-line arguments.
        2. If not, extracts them from feature file markers.
        3. Creates a new test run if project_id and suite_id exist.

        Args:
            session (pytest.Session): The pytest session object.
        """
        Logger.info("Collecting all tests and getting all testrail caseid's...")

        if self.run_id:
            Logger.info(
                f"Already run exisits, using run: {self.run_id} for updating the test results..."
            )
            return  # Exit early since a run already exists
        # Extract project_id and suite_id if not already provided
        if not (self.project_id and self.suite_id) and session.items:
            item = session.items[0]
            self.project_id = self.get_id_from_marker(
                item=item, marker_prefix="projectid"
            )
            self.suite_id = self.get_id_from_marker(
                item=item, marker_prefix="suiteid"
            )

        # Create a new test run if both project_id and suite_id are available
        if self.project_id and self.suite_id:
            case_ids = []
            for item in session.items:
                case_id = self.get_id_from_marker(item=item, marker_prefix="caseid")
                if case_id:
                    case_ids.append(case_id.lstrip("C"))
            self.run_id = self.add_run(case_ids=case_ids)
        else:
            Logger.warning(
                "Skipping test run creation due to missing project_id or suite_id."
            )

    @pytest.hookimpl(hookwrapper=True)
    def pytest_runtest_makereport(self, item, call):
        """
        This hook is triggered after each test to collect the result and
        check if it has a 'caseid' marker. If present, it updates TestRail
        with the test result.

        Args:
            item (pytest.Item): The test case item.
            call (pytest.CallInfo): The result of the test execution.
        """
        outcome = yield
        report = outcome.get_result()
        # capturing the actual test results
        # report the testcase results when only run id exists
        if report.when == "call" and self.run_id:
            # Check if the test case has a @caseid marker
            case_id = self.get_id_from_marker(item=item, marker_prefix="caseid")
            case_id = case_id.lstrip("C")

            if case_id:
                # Determine test result status (1 = passed, 5 = failed)
                status = 5 if report.failed else 1
                elapsed_time = report.duration  # Get elapsed time in seconds
                message = [
                    f"Test case '{item.name}' {'passed' if status == 1 else 'failed'}.",
                    f"{20 * '='}",
                ]

                # If the test failed, capture the stack trace
                if status == 5:
                    message.append(f"Failure Trace:\n{report.longreprtext}")

                message.append(f"\n\n{100 * '='}")

                # Give steps wise results
                if report.scenario:
                    message.append(
                        f"{self.get_scenario_step_wise_status(report.scenario)}"
                    )

                # Update TestRail with the test result
                self.add_test_case_result_to_run(
                    case_id, status, "\n".join(message), elapsed_time
                )


def pytest_addoption(parser):
    """
    Adds command-line options for the TestRail reporter plugin.

    Args:
        parser (pytest.Parser): The pytest argument parser.
    """
    group = parser.getgroup("TestRail reporter plugin")

    # All arguments are now optional, with default values set to None.
    group.addoption(
        "--report-testrail",
        action="store_true",
        help="Enable TestRail reporting.",
        default=False,  # By default not enabling reporting to the testrail
    )
    group.addoption(
        "--testrail-url",
        action="store",
        type=str,
        help="The URL of the TestRail instance.",
        default="https://liveramp.testrail.io",
    )
    group.addoption(
        "--user-name",
        action="store",
        type=str,
        help="TestRail username. This is mandatory field pass it either from command line or set env variable as 'TESTRAIL_USERNAME'",
        default=os.getenv("TESTRAIL_USERNAME", None),
    )
    group.addoption(
        "--password",
        action="store",
        type=str,
        help="TestRail password. This is mandatory field pass it either from command line or set env variable as 'TESTRAIL_API_KEY'",
        default=os.getenv("TESTRAIL_API_KEY", None),
    )
    group.addoption(
        "--project-id",
        action="store",
        type=int,
        help="""
        The ID of the TestRail project. This value can be passed in 3ways
        1. pass from command line
        2. set env variable as 'PROJECT_ID'
        3. Set Marker in feature file as @projectid:<project_id>
        """,
        default=os.getenv("PROJECT_ID", None),
    )
    group.addoption(
        "--suite-id",
        action="store",
        type=int,
        help="""
        The ID of the TestRail project. This value can be passed in 3ways
        1. pass from command line
        2. set env variable as 'SUITE_ID'
        3. Set Marker in feature file as @suiteid:<suite_id>
        """,
        default=os.getenv("SUITE_ID", None),
    )
    group.addoption(
        "--run-id",
        action="store",
        type=int,
        help="The ID of an existing TestRail test run. If passed all the results will be added to this run",
        default=os.getenv("RUN_ID", None),
    )
    group.addoption(
        "--run-name",
        action="store",
        type=str,
        help="The name of the test run. This is not applicable for existing runs",
        default=None,
    )


def pytest_configure(config: pytest.Config):
    """
    Configures the TestRail reporter plugin.

    Registers the plugin if `--report-testrail` is provided and required credentials exist.

    Args:
        config (pytest.Config): The pytest configuration object.
    """
    # Registers the plugin if `--report-testrail` is provided
    if not config.getoption("--report-testrail"):
        # Not registering testrail reporter plugin ...
        return
    reporter = TestrailReporter(config)
    reporter.testrail_url = config.getoption("testrail_url")
    reporter.user_name = config.getoption("user_name")
    reporter.password = config.getoption("password")
    reporter.project_id = config.getoption("project_id")
    reporter.suite_id = config.getoption("suite_id")
    reporter.run_id = config.getoption("run_id")
    reporter.run_name = config.getoption("run_name")

    if reporter.user_name and reporter.password:
        Logger.info("Registering testrail reporter plugin ...")
        config.pluginmanager.register(reporter)
    else:
        Logger.warning(
            "Not registering testrail reporter plugin as username/password are not given..."
        )
