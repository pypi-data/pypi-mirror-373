import pytest
from unittest.mock import patch, MagicMock
from liveramp_automation.utils.pagerduty import PagerDutyClient


class TestPagerDutyClient:
    @patch('liveramp_automation.utils.pagerduty.requests')
    def test_trigger_incident_basic(self, mock_requests):
        client = PagerDutyClient('fake_api_key')
        mock_response = MagicMock()
        mock_response.json.return_value = {'incident': {'id': 'fake_incident_id', 'status': 'fake_status'}}
        mock_requests.post.return_value = mock_response

        incident_id, incident_status = client.trigger_incident('fake_service_id', 'fake_summary')
        assert incident_id == 'fake_incident_id'
        assert incident_status == 'fake_status'

    @patch('liveramp_automation.utils.pagerduty.requests')
    def test_trigger_incident_with_details(self, mock_requests):
        client = PagerDutyClient('fake_api_key')
        mock_response = MagicMock()
        mock_response.json.return_value = {'incident': {'id': 'fake_incident_id', 'status': 'fake_status'}}
        mock_requests.post.return_value = mock_response

        details = {'key': 'value'}
        incident_id, incident_status = client.trigger_incident('fake_service_id', 'fake_summary', details=details)
        assert incident_id == 'fake_incident_id'
        assert incident_status == 'fake_status'

    @patch('liveramp_automation.utils.pagerduty.requests')
    def test_trigger_incident_with_dedup_key(self, mock_requests):
        client = PagerDutyClient('fake_api_key')
        mock_response = MagicMock()
        mock_response.json.return_value = {'incident': {'id': 'fake_incident_id', 'status': 'fake_status'}}
        mock_requests.post.return_value = mock_response

        dedup_key = 'fake_dedup_key'
        incident_id, incident_status = client.trigger_incident('fake_service_id', 'fake_summary', dedup_key=dedup_key)
        assert incident_id == 'fake_incident_id'
        assert incident_status == 'fake_status'

    @patch('liveramp_automation.utils.pagerduty.requests')
    def test_trigger_incident_with_escalation_policy_id(self, mock_requests):
        client = PagerDutyClient('fake_api_key')
        mock_response = MagicMock()
        mock_response.json.return_value = {'incident': {'id': 'fake_incident_id', 'status': 'fake_status'}}
        mock_requests.post.return_value = mock_response

        escalation_policy_id = 'fake_escalation_policy_id'
        incident_id, incident_status = client.trigger_incident('fake_service_id', 'fake_summary',
                                                               escalation_policy_id=escalation_policy_id)
        assert incident_id == 'fake_incident_id'
        assert incident_status == 'fake_status'

    @patch('liveramp_automation.utils.pagerduty.requests')
    def test_trigger_incident_with_assignee(self, mock_requests):
        client = PagerDutyClient('fake_api_key')
        mock_response = MagicMock()
        mock_response.json.return_value = {'incident': {'id': 'fake_incident_id', 'status': 'fake_status'}}
        mock_requests.post.return_value = mock_response

        assignee = 'fake_assignee'
        incident_id, incident_status = client.trigger_incident('fake_service_id', 'fake_summary', assignee=assignee)
        assert incident_id == 'fake_incident_id'
        assert incident_status == 'fake_status'

    @patch('liveramp_automation.utils.pagerduty.requests')
    def test_acknowledge_incident(self, mock_requests):
        client = PagerDutyClient('fake_api_key')
        mock_response = MagicMock()
        mock_response.json.return_value = {'incident': {'status': 'acknowledged'}}
        mock_requests.put.return_value = mock_response

        result = client.acknowledge_incident('fake_incident_id')
        assert result == "acknowledged"

    @patch('liveramp_automation.utils.pagerduty.requests')
    def test_resolve_incident(self, mock_requests):
        client = PagerDutyClient('fake_api_key')
        mock_response = MagicMock()
        mock_response.json.return_value = {'incident': {'status': 'resolved'}}
        mock_requests.put.return_value = mock_response

        result = client.resolve_incident('fake_incident_id')
        assert result == "resolved"

    @patch('liveramp_automation.utils.pagerduty.requests')
    def test_list_open_incidents(self, mock_requests):
        client = PagerDutyClient('fake_api_key')
        mock_response = MagicMock()
        mock_response.json.return_value = {'incidents': [{'id': 'fake_incident_id', 'html_url': 'fake_url'}]}
        mock_requests.get.return_value = mock_response

        incidents = client.list_open_incidents('fake_service_id')
        assert len(incidents) == 1
        assert incidents[0]['id'] == 'fake_incident_id'
        assert incidents[0]['url'] == 'fake_url'
