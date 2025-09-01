from typing import Optional, Dict, Any, Sequence, List, Tuple
from liveramp_automation.utils.slack import SlackHTMLParser, SlackWebhook, WebhookResponse, SlackBot
from liveramp_automation.utils.pagerduty import PagerDutyClient


class NotificationHelper:
    @staticmethod
    def slack_webhook_notify(*,
                             webhook_url: str,
                             message: str,
                             attachments: Optional[Sequence[Dict[str, Any]]] = None,
                             blocks: Optional[Sequence[Dict[str, Any]]] = None,
                             parsed_html_flag: Optional[bool] = False) -> WebhookResponse:
        """Sends a message to the webhook URL.

        Args:
            message: Plain text string to send to Slack.
            attachments: A collection of attachments
            blocks: A collection of Block Kit UI components
            parsed_html_flag: A flag indicates whether need parse the parameter message, otherwise send the message to Slack directly. default: False

        Returns:
            Webhook response

        Example:
        WEBHOOk_URL = "https://hooks.slack.com/services/xxxxx/xxxxxx/xxxxxx"
        html_string = '''
            <p>
                Here <i>is</i> a <strike>paragraph</strike> with a <b>lot</b> of formatting.
            </p>
            <br>
            <code>Code sample</code> & testing escape.
            <ul>
                <li>
                    <a href="https://www.google.com">Google</a>
                </li>
                <li>
                    <a href="https://www.amazon.com">Amazon</a>
                </li>
            </ul>
        '''
        blocks = [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "New request"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*Type:*\nPaid Time Off"
                        },
                        {
                            "type": "mrkdwn",
                            "text": "*Created by:*\n<example.com|Fred Enriquez>"
                        }
                    ]
                },
                {
                    "type": "section",
                    "fields": [
                        {
                            "type": "mrkdwn",
                            "text": "*When:*\nAug 10 - Aug 13"
                        }
                    ]
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": "<https://example.com|View request>"
                    }
                }
            ]

        attachments = [
            {
                "fallback": "Plain-text summary of the attachment.",
                "color": "#2eb886",
                "pretext": "Optional text that appears above the attachment block",
                "author_name": "Bobby Tables",
                "author_link": "http://flickr.com/bobby/",
                "author_icon": "http://flickr.com/icons/bobby.jpg",
                "title": "Slack API Documentation",
                "title_link": "https://api.slack.com/",
                "text": "Optional text that appears within the attachment",
                "fields": [
                    {
                        "title": "Priority",
                        "value": "High",
                        "short": False
                    }
                ],
                "image_url": "http://my-website.com/path/to/image.jpg",
                "thumb_url": "http://example.com/path/to/thumb.png",
                "footer": "Slack API",
                "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
                "ts": 123456789
            }
        ]
        NotificationHelper.slack_notify(webhook_url=WEBHOOk_URL, message="test")
        NotificationHelper.slack_notify(webhook_url=WEBHOOk_URL, message=html_string, parsed_html_flag=True)
        NotificationHelper.slack_notify(webhook_url=WEBHOOk_URL, message="test", attachments=attachments, blocks=blocks)
        :param webhook_url:
        """
        client = SlackWebhook(url=webhook_url)
        if parsed_html_flag:
            parser = SlackHTMLParser()
            message = parser.parse(message)
        return client.send(message=message, attachments=attachments, blocks=blocks)

    @staticmethod
    def send_message_to_channels(token: str, channels: List[str], message: str) -> Dict[str, Tuple[bool, str]]:
        """
        Send a message to multiple channels.

        Args:
            token (str): The Slack token.
            channels (List[str]): A list of channel IDs.
            message (str): Plain text string to send to Slack.

        Returns:
            A dictionary mapping channel IDs to a tuple of success status and error message (if any).
        """
        # Create an instance of SlackBot with the provided token
        slack_bot = SlackBot(token=token, timeout=15)

        # Call send_message_to_channels method
        return slack_bot.send_message_to_channels(channels, message)

    @staticmethod
    def reply_latest_message(token: str, channel_id: str, message: str) -> bool:
        """
        Reply to the latest message in a channel.

        Args:
            token (str): The Slack token.
            channel_id (str): ID of the channel to reply to.
            message (str): Plain text string to send to Slack.

        Returns:
            A boolean indicating success or failure of the reply operation.
        """
        # Create an instance of SlackBot with the provided token
        slack_bot = SlackBot(token=token, timeout=15)

        # Call reply_latest_message method
        return slack_bot.reply_latest_message(channel_id, message)

    @staticmethod
    def pagerduty_notify(api_key: str, service_id: str, summary: str, details: dict = None, dedup_key: str = None,
                         escalation_policy_id: str = None, assignee: str = None) -> Tuple[Optional[str], Optional[str]]:
        """
        Static method to trigger an incident notification using PagerDuty.

        Args:
            api_key (str): The PagerDuty API key.
            service_id (str): The ID of the PagerDuty service to trigger the incident on.
            summary (str): Summary or title of the incident.
            details (dict, optional): Additional details about the incident. Defaults to None.
            dedup_key (str, optional): A unique key to deduplicate incidents. Defaults to None.
            escalation_policy_id (str, optional): The ID of the escalation policy to assign to the incident. Defaults to None.
            assignee (str, optional): The ID of the user to assign the incident to. Defaults to None.

        Returns:
            Tuple[Optional[str], Optional[str]]: A tuple containing the ID and status of the triggered incident.
        """
        pagerduty_client = PagerDutyClient(api_key)
        return pagerduty_client.trigger_incident(service_id, summary, details, dedup_key, escalation_policy_id,
                                                 assignee)

    @staticmethod
    def acknowledge_incident(api_key: str, incident_id: str) -> bool:
        """
        Static method to acknowledge an incident using PagerDuty.

        Args:
            api_key (str): The PagerDuty API key.
            incident_id (str): The ID of the incident to acknowledge.

        Returns:
            bool: True if the incident is acknowledged successfully, False otherwise.
        """
        pagerduty_client = PagerDutyClient(api_key)
        return pagerduty_client.acknowledge_incident(incident_id)

    @staticmethod
    def resolve_incident(api_key: str, incident_id: str) -> bool:
        """
        Static method to resolve an incident using PagerDuty.

        Args:
            api_key (str): The PagerDuty API key.
            incident_id (str): The ID of the incident to resolve.

        Returns:
            bool: True if the incident is resolved successfully, False otherwise.
        """
        pagerduty_client = PagerDutyClient(api_key)
        return pagerduty_client.resolve_incident(incident_id)

    @staticmethod
    def list_incidents(api_key: str, service_id: str) -> List[Dict[str, str]]:
        """
        Static method to list incidents in a PagerDuty service.

        Args:
            api_key (str): The PagerDuty API key.
            service_id (str): The ID of the PagerDuty service to list incidents for.

        Returns:
            List[Dict[str, str]]: A list of dictionaries containing the ID and URL of each incident.
        """
        pagerduty_client = PagerDutyClient(api_key)
        return pagerduty_client.list_open_incidents(service_id)

    def oc_notify(self):
        return

    @staticmethod
    def deal_enqueue(api_key: str,
                     service_id: str,
                     event_action: str,
                     summary: str,
                     source: str,
                     dedup_key: str = None,
                     custom_details: dict = None,
                     critical: str = "critical"
                     ):
        """
        Static method to send PagerDuty a trigger event to report a new problem,
        or update an ongoing problem, depending on the event type.
        https://developer.pagerduty.com/api-reference/368ae3d938c9e-send-an-event-to-pager-duty
        Args:
            api_key (str): This is the "Integration Key" listed on the Events API V2 integration's detail page.
            service_id (str): The ID of the PagerDuty service to trigger the incident on.
            event_action (str): The type of event. Can be trigger, acknowledge or resolve.
            summary (str): Summary or title of the incident.
            source (str): The unique location of the affected system, preferably a hostname or FQDN
            custom_details (dict, optional): Additional details about the event and affected system. Defaults to None.
            dedup_key (str, optional): The unique value to differ events.
            critical (str, optional): Allowed values: critical,warning,error,info. Defaults to "critical".
        """
        pagerduty_client = PagerDutyClient(api_key)
        return pagerduty_client.deal_enqueue(service_id, event_action, dedup_key, summary,
                                             source, custom_details, critical)
