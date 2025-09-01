import pytest
from unittest.mock import MagicMock, patch
from liveramp_automation.plugins.test_rail_report_plugin import TestrailReporter


@pytest.fixture
def testrail_reporter(request):
    """Fixture to create and return a TestrailReporter instance with test values."""
    reporter = TestrailReporter(request.config)

    # Assign values explicitly for testing
    reporter.testrail_url = "https://testrail-example.com"
    reporter.user_name = "testuser"
    reporter.password = "mockpassword"
    reporter.project_id = 124
    reporter.suite_id = 456
    # Mock session object and its `post` method
    reporter.session = MagicMock()
    reporter.session.post = MagicMock()
    reporter.session.get = MagicMock()
    yield reporter


def test_get_project_name(testrail_reporter):
    """Test fetching project name"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"name": "Mock Project"}
    with patch.object(testrail_reporter, "session", create=True) as mock_session:
        mock_session.get.return_value = mock_response
        project_name = testrail_reporter.get_project_name()
    assert project_name == "Mock Project"


def test_get_empty_project_name(testrail_reporter):
    """Test fetching project name"""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.ok = False
    mock_response.json.return_value = {"error": "error while getting projectname"}
    with patch.object(testrail_reporter, "session", create=True) as mock_session:
        mock_session.get.return_value = mock_response
        project_name = testrail_reporter.get_project_name()
    assert not project_name, "project name should be empty"


def test_get_suite_name(testrail_reporter):
    """Test fetching suite name"""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"name": "Mock Suite"}
    with patch.object(testrail_reporter, "session", create=True) as mock_session:
        mock_session.get.return_value = mock_response
        suite_name = testrail_reporter.get_suite_name()
    assert suite_name == "Mock Suite"


def test_get_empty_suite_name(testrail_reporter):
    """Test fetching suite name"""
    mock_response = MagicMock()
    mock_response.status_code = 400
    mock_response.ok = False
    mock_response.json.return_value = {"error": "error while getting suitename"}
    with patch.object(testrail_reporter, "session", create=True) as mock_session:
        mock_session.get.return_value = mock_response
        suite_name = testrail_reporter.get_suite_name()
    assert not suite_name, "suite name should be empty"


@pytest.mark.parametrize(
    "marker_name, marker_value",
    [("projectid", "17"), ("suiteid", "197"), ("caseid", "12345")],
)
def test_marker_extraction(request, marker_name, marker_value):
    """Test that different markers (projectid, suiteid, caseid) are correctly extracted."""

    reporter = TestrailReporter(request.config)

    # Mocking pytest.Item
    mock_item = MagicMock()
    mock_marker = MagicMock()

    # Setting up the marker name
    mock_marker.name = f"{marker_name}:{marker_value}"
    mock_item.iter_markers.return_value = [mock_marker]

    extracted_value = reporter.get_id_from_marker(mock_item, marker_name)

    assert extracted_value == marker_value, (
        f"Expected '{marker_value}' but got {extracted_value}"
    )


def test_invalid_marker_extraction(request):
    """Test that different markers (projectid, suiteid, caseid) are correctly extracted."""

    reporter = TestrailReporter(request.config)

    # Mocking pytest.Item
    mock_item = MagicMock()
    mock_marker = MagicMock()

    # Setting up the marker name
    mock_marker.name = "caseid"
    mock_item.iter_markers.return_value = [mock_marker]

    extracted_value = reporter.get_id_from_marker(mock_item, "caseid")
    assert not extracted_value, "Null extractor value should be returned"


def test_get_scenario_step_wise_status_basic(testrail_reporter):
    """Test a basic scenario with feature, scenario, and passing steps"""
    scenario_data = {
        "feature": {"name": "Login Feature", "filename": "login.feature"},
        "name": "Successful Login",
        "steps": [
            {"keyword": "Given", "name": "user is on login page"},
            {"keyword": "When", "name": "user enters valid credentials"},
            {"keyword": "Then", "name": "user should see dashboard"},
        ],
    }

    expected_output = """Feature: Login Feature (login.feature)

\tScenario: Successful Login
\t\tSteps:
\t\t\tGiven user is on login page - PASSED
\t\t\tWhen user enters valid credentials - PASSED
\t\t\tThen user should see dashboard - PASSED"""

    output = testrail_reporter.get_scenario_step_wise_status(scenario_data)
    assert output.strip() == expected_output.strip()


def test_get_scenario_step_wise_status_missing_fields(testrail_reporter):
    """Test a scenario with missing optional fields"""
    scenario_data = {
        "name": "No Feature or Rule",
        "steps": [
            {"keyword": "Given", "name": "some setup"},
        ],
    }

    expected_output = """Feature: Unknown (N/A)

\tScenario: No Feature or Rule
\t\tSteps:
\t\t\tGiven some setup - PASSED"""

    output = testrail_reporter.get_scenario_step_wise_status(scenario_data)
    assert output.strip() == expected_output.strip()


def test_get_scenario_step_wise_status_with_failures(testrail_reporter):
    """Test a scenario where some steps fail"""
    scenario_data = {
        "feature": {"name": "Payment Feature", "filename": "payment.feature"},
        "name": "Payment Declined",
        "steps": [
            {"keyword": "Given", "name": "user has a valid card"},
            {
                "keyword": "When",
                "name": "user tries to make payment",
                "failed": True,
                "error_message": "Insufficient funds",
            },
            {"keyword": "Then", "name": "payment should be successful", "failed": True},
        ],
    }

    expected_output = """Feature: Payment Feature (payment.feature)

\tScenario: Payment Declined
\t\tSteps:
\t\t\tGiven user has a valid card - PASSED
\t\t\tWhen user tries to make payment - FAILED
\t\t\t\tError: Insufficient funds
\t\t\tThen payment should be successful - FAILED"""

    output = testrail_reporter.get_scenario_step_wise_status(scenario_data)
    assert output.strip() == expected_output.strip()


def test_get_scenario_step_wise_status_with_rule(testrail_reporter):
    """Test a scenario that includes a rule"""
    scenario_data = {
        "feature": {"name": "Profile Feature", "filename": "profile.feature"},
        "name": "Update Profile",
        "rule": {"name": "Only logged-in users can update profile"},
        "steps": [
            {"keyword": "Given", "name": "user is logged in"},
            {"keyword": "When", "name": "user updates profile"},
            {"keyword": "Then", "name": "profile should be updated"},
        ],
    }

    expected_output = """Feature: Profile Feature (profile.feature)

\tScenario: Update Profile
\t\tRule: Only logged-in users can update profile

\t\tSteps:
\t\t\tGiven user is logged in - PASSED
\t\t\tWhen user updates profile - PASSED
\t\t\tThen profile should be updated - PASSED"""

    output = testrail_reporter.get_scenario_step_wise_status(scenario_data)
    assert output.strip() == expected_output.strip()


def test_get_scenario_step_wise_status_no_steps(testrail_reporter):
    """Test a scenario with no steps"""
    scenario_data = {
        "feature": {"name": "Empty Feature", "filename": "empty.feature"},
        "name": "No Steps Scenario",
    }

    expected_output = """Feature: Empty Feature (empty.feature)

\tScenario: No Steps Scenario
\t\tSteps:"""  # No steps present

    output = testrail_reporter.get_scenario_step_wise_status(scenario_data)
    assert output.strip() == expected_output.strip()


@pytest.fixture
def mock_session():
    """Mock pytest session object"""
    session = MagicMock()
    session.items = []
    return session
