import base64
from unittest.mock import Mock, patch

import pytest
import requests

from liveramp_automation.utils.slack import SlackHTMLParser, WebhookResponse, SlackWebhook, SlackBot, TimeoutError, \
    CommunicationError

WEBHOOK_URL = "aHR0cHM6Ly9ob29rcy5zbGFjay5jb20vc2VydmljZXMvVDI4SkVROVJWL0IwN0hFN1pGTTBYL2c1OUc5UDBHMDlXeEJZVzJweUVQQXpQVQ=="
BOT_USER = "eG94Yi03NjYyNjgyNTg3OS0zMzU3MjM2MjU5MzkyLTAzYlBDMmZleUhIa21Gc3ExNXc5dzFocw=="
CHANNEL_NAME = "qe_test"
CHANNEL_ID = "C034YU3NKRP"
CHANNEL_IDS = ["C034YU3NKRP", "C07HUQ4ELBC", "GTEQBLWN8"]
TEST_MESSAGE = "This is a new test message from the LiveRamp Automation Framework"
TEST_MESSAGE_REPLY = "This is another test message from the LiveRamp Automation Framework"
MESSAGE_SIZE = 2

html_string_sample = '''
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
html_string_illegal_sample = '''
    <y>
        Here <s>is</s> a <strike>paragraph</strike> with a <b>lot</b> of formatting.
    </y>
'''

blocks_sample = [
    {
        "type": "header",
        "text": {
            "type": "plain_text",
            "text": "This is a new request by automation-framework"
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

attachments_sample = [
    {
        "fallback": "Plain-text summary of the attachment.",
        "color": "#2eb886",
        "pretext": "Optional text that appears above the attachment block",
        "author_name": "Bobby Tables",
        "author_link": "https://flickr.com/bobby/",
        "author_icon": "https://flickr.com/icons/bobby.jpg",
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
        "image_url": "https://my-website.com/path/to/image.jpg",
        "thumb_url": "https://example.com/path/to/thumb.png",
        "footer": "Slack API",
        "footer_icon": "https://platform.slack-edge.com/img/default_application_icon.png",
        "ts": 123456789
    }
]


@pytest.fixture
def slack_client():
    return SlackWebhook(url=base64.b64decode(WEBHOOK_URL).decode())


@pytest.fixture
def slack_bot_instance():
    return SlackBot(token=base64.b64decode(BOT_USER).decode(), timeout=15)


@pytest.fixture
def slack_mock():
    slack_mock = Mock()
    slack_mock.url = 'https://liveramp.com/careers/'
    slack_mock.title = 'Liveramp'
    return slack_mock


def assert_res(res: WebhookResponse):
    assert 200 == res.status_code
    assert 'ok' == res.body


def test_send_message(slack_client):
    res = slack_client.send(message="Liveramp Automation Framework Testing")
    assert_res(res)


def test_send_parsed_html(slack_client):
    parser = SlackHTMLParser()
    parsed_message = parser.parse(html_string_sample)
    res = slack_client.send(message=parsed_message)
    assert_res(res)


def test_send_unparsed_html(slack_client):
    parser = SlackHTMLParser()
    parsed_message = parser.parse(html_string_illegal_sample)
    res = slack_client.send(message=parsed_message)
    assert_res(res)


def test_send_block(slack_client):
    res = slack_client.send(message="blocks", blocks=blocks_sample)
    assert_res(res)


def test_send_attachments(slack_client):
    res = slack_client.send(message="attachments", attachments=attachments_sample)
    assert_res(res)


def test_send_timeout_error(slack_client):
    with patch("liveramp_automation.utils.slack.requests.post") as mock_post:
        mock_post.side_effect = requests.Timeout

        with pytest.raises(TimeoutError):
            slack_client.send(message="Test message")


def test_send_communication_error(slack_client):
    with patch("liveramp_automation.utils.slack.requests.post") as mock_post:
        mock_post.side_effect = requests.RequestException("Mocked request exception")

        with pytest.raises(CommunicationError):
            slack_client.send(message="Test message")


def test_send_http_error(slack_client):
    with patch("liveramp_automation.utils.slack.requests.post") as mock_post:
        mock_post.return_value.status_code = 404
        mock_post.return_value.text = "Not Found"

        response = slack_client.send(message="Test message")
        assert response.status_code == 404
        assert response.body == "Not Found"


def test_send_message_success(slack_bot_instance):
    result = slack_bot_instance.send_message(CHANNEL_ID, TEST_MESSAGE)
    assert result == (True, "")


def test_send_message_failure(slack_bot_instance):
    with patch("liveramp_automation.utils.slack.requests.post") as mock_post:
        mock_post.return_value.status_code = 400
        mock_post.return_value.json.return_value = {"ok": False, "error": "channel_not_found"}

        success, error = slack_bot_instance.send_message(channel_id="test_channel_id", message="Test message")
        assert success is False
        assert error == "channel_not_found"


def test_get_latest_n_messages(slack_bot_instance):
    result = slack_bot_instance.get_latest_n_messages(CHANNEL_ID, limit=MESSAGE_SIZE)
    assert result['ok']
    assert len(result['messages']) == MESSAGE_SIZE


def test_reply_latest_message(slack_bot_instance):
    result = slack_bot_instance.reply_latest_message(CHANNEL_ID, TEST_MESSAGE_REPLY)
    assert result is True


def test_reply_latest_message_no_message_to_reply(slack_bot_instance):
    with patch.object(slack_bot_instance, 'get_latest_n_messages') as mock_get_latest:
        mock_get_latest.return_value = {"messages": []}

        response = slack_bot_instance.reply_latest_message(channel_id="test_channel_id", message="Test reply")
        assert response is False


def test_send_message_to_channels(slack_bot_instance):
    result = slack_bot_instance.send_message_to_channels(CHANNEL_IDS, TEST_MESSAGE)
    assert result
