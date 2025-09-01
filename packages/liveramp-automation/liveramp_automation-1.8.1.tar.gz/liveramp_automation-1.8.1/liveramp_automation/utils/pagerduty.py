import datetime

import requests
from typing import Optional, Dict, Any, Tuple, List
from liveramp_automation.utils.log import Logger


class PagerDutyClient:
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'Accept': 'application/vnd.pagerduty+json;version=2',
            'Authorization': f'Token token={api_key}',
            'Content-Type': 'application/json'
        }
        self.base_url = 'https://api.pagerduty.com'
        self.event_url = 'https://events.pagerduty.com'

    def _update_incident_status(self, incident_id: str, status: str) -> str:
        endpoint = f'{self.base_url}/incidents/{incident_id}'
        payload = {
            "incident": {
                "type": "incident",
                "status": status
            }
        }

        Logger.debug(f"Sending a request - url: {endpoint}, payload: {payload}, headers: {self.headers}")
        response = requests.put(endpoint, json=payload, headers=self.headers)
        response.raise_for_status()
        Logger.debug(f"Received the response: {response.json()}")
        return response.json()['incident']['status']

    def trigger_incident(self, service_id: str, summary: str, details: Optional[Dict[str, Any]] = None,
                         dedup_key: Optional[str] = None, escalation_policy_id: Optional[str] = None,
                         assignee: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        endpoint = f'{self.base_url}/incidents'
        payload = {
            "incident": {
                "type": "incident",
                "title": summary,
                "service": {
                    "id": service_id,
                    "type": "service_reference"
                }
            }
        }
        if details:
            payload['incident']['body'] = {
                "type": "incident_body",
                "details": details
            }
        if dedup_key:
            payload['dedup_key'] = dedup_key
        if escalation_policy_id:
            payload['incident']['escalation_policy'] = {
                "id": escalation_policy_id,
                "type": "escalation_policy_reference"
            }
        if assignee:
            payload['incident']['assignments'] = [{
                "assignee": {
                    "id": assignee,
                    "type": "user_reference"
                }
            }]
        Logger.debug(f"Sending a request - url: {endpoint}, payload: {payload}, headers: {self.headers}")
        response = requests.post(endpoint, json=payload, headers=self.headers)
        response.raise_for_status()
        Logger.debug(f"Received the response: {response.json()}")
        incident_data = response.json().get('incident')
        incident_id = incident_data.get('id') if incident_data else None
        incident_status = incident_data.get('status') if incident_data else None
        return incident_id, incident_status

    def acknowledge_incident(self, incident_id: str) -> str:
        return self._update_incident_status(incident_id, "acknowledged")

    def resolve_incident(self, incident_id: str) -> str:
        return self._update_incident_status(incident_id, "resolved")

    def list_open_incidents(self, service_id: str) -> List[Dict[str, str]]:
        endpoint = f'{self.base_url}/incidents'
        payload = {
            'service_ids[]': service_id,
            'statuses[]': ['triggered', 'acknowledged']
            # 'include[]': 'assignees'    # Optional, include assignees in the response
        }

        Logger.debug(f"Sending a request - url: {endpoint}, payload: {payload}, headers: {self.headers}")
        response = requests.get(endpoint, params=payload, headers=self.headers)
        response.raise_for_status()
        Logger.debug(f"Received the response: {response.json()}")
        incidents = response.json().get('incidents', [])
        incident_list = [{'id': incident['id'], 'url': incident['html_url']} for incident in incidents]
        return incident_list

    def deal_enqueue(self,
                     service_id: str,
                     event_action: str,
                     dedup_key: str,
                     summary: str,
                     source: str,
                     custom_details: Optional[Dict[str, Any]] = None,
                     severity="critical"):
        endpoint = f'{self.event_url}/v2/enqueue'
        json_data = {
            "dedup_key": dedup_key,
            "event_action": event_action,
            "payload": {
                "severity": severity,
                "summary": summary,
                "source": source
            },
            "routing_key": service_id
        }

        if custom_details:
            json_data["payload"]['custom_details'] = custom_details

        Logger.debug(f"Sending a request - url: {endpoint}, payload: {json_data}, headers: {self.headers}")
        response = requests.post(endpoint, json=json_data, headers=self.headers)
        return response
