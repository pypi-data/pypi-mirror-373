import pytest
from unittest.mock import MagicMock
from liveramp_automation.utils.slack import WebhookResponse
from liveramp_automation.helpers.notification import NotificationHelper

class TestNotificationHelper:
    @pytest.fixture
    def mock_slack_webhook(self, monkeypatch):
        mock_send = MagicMock(return_value=WebhookResponse(status_code=200, body="OK"))
        monkeypatch.setattr("liveramp_automation.utils.slack.SlackWebhook.send", mock_send)
        yield mock_send

    def test_slack_webhook_notify_plain_text(self, mock_slack_webhook):
        # Test sending plain text message
        webhook_url = "https://hooks.slack.com/services/xxxxx/xxxxxx/xxxxxx"
        message = "Test plain text message"
        response = NotificationHelper.slack_webhook_notify(webhook_url=webhook_url, message=message)
        assert response.status_code == 200
        assert response.body == "OK"
        mock_slack_webhook.assert_called_once_with(message=message, attachments=None, blocks=None)

    # Add more tests for different scenarios of slack_webhook_notify method

    def test_send_message_to_channels(self, monkeypatch):
        # Test sending message to multiple channels
        token = "your_slack_token"
        channels = ["channel_id_1", "channel_id_2"]
        message = "Test message"
        expected_result = {
            "channel_id_1": (True, ""),
            "channel_id_2": (True, "")
        }

        mock_send_message_to_channels = MagicMock(return_value=expected_result)
        monkeypatch.setattr("liveramp_automation.utils.slack.SlackBot.send_message_to_channels", mock_send_message_to_channels)

        result = NotificationHelper.send_message_to_channels(token, channels, message)
        assert result == expected_result

    def test_reply_latest_message(self, monkeypatch):
        # Test replying to the latest message in a channel
        token = "your_slack_token"
        channel_id = "channel_id"
        message = "Test reply message"
        expected_result = True

        mock_reply_latest_message = MagicMock(return_value=expected_result)
        monkeypatch.setattr("liveramp_automation.utils.slack.SlackBot.reply_latest_message", mock_reply_latest_message)

        result = NotificationHelper.reply_latest_message(token, channel_id, message)
        assert result == expected_result

    def test_slack_webhook_notify_with_parsed_html_flag(self, monkeypatch, mock_slack_webhook):
        # Test slack_webhook_notify with parsed_html_flag=True
        webhook_url = "https://hooks.slack.com/services/xxxxx/xxxxxx/xxxxxx"
        html_message = "<p>Test HTML message</p>"
        parsed_message = "Test HTML message"
        attachments = None
        blocks = None

        # Mock the SlackHTMLParser.parse method
        mock_parse = MagicMock(return_value=parsed_message)
        monkeypatch.setattr("liveramp_automation.utils.slack.SlackHTMLParser.parse", mock_parse)

        response = NotificationHelper.slack_webhook_notify(webhook_url=webhook_url,
                                                           message=html_message,
                                                           parsed_html_flag=True)

        assert response.status_code == 200
        assert response.body == "OK"
        mock_slack_webhook.assert_called_once_with(message=parsed_message, attachments=attachments, blocks=blocks)
        mock_parse.assert_called_once_with(html_message)

    # To Do: Add tests for the remaining methods (pagerduty_notify, oc_notify)
