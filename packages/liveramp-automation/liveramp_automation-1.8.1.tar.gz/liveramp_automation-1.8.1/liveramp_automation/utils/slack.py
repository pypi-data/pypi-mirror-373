import re
import requests
from requests import Response
from html.parser import HTMLParser
from typing import Optional, Dict, Any, Tuple, List, Sequence
from liveramp_automation.utils.log import Logger


class SlackHTMLParser(HTMLParser):
    def __init__(self, *args, **kwargs):
        """Escapes and converts an HTML string to Slack flavored Markdown.
        More about Slack's Markdown Flavor (mrkdwn) can be seen here:
            https://api.slack.com/reference/surfaces/formatting
        """
        super().__init__(*args, **kwargs)
        self.slack_message = ''
        self.ignore_tag = False
        self.line_break = '::LINE::BREAK::'

    def handle_starttag(self, tag: str, attrs: List[Tuple[str, Any]]):
        """ Called when the opening of a tag is encountered.

        Args:
            tag: Lowercase name of the HTML tag.  E.G. `br` or `i`.
            attrs: List of tuples with the tuple having the following form:
            (attribute name, value).  E.G. ('href', 'www.example.com').
        """
        if tag in ['i', 'em']:
            self.slack_message += '_'
        elif tag in ['b', 'strong']:
            self.slack_message += '*'
        elif tag == 'strike':
            self.slack_message += '~'
        elif tag in ['br', 'p', 'ul']:
            self.slack_message += self.line_break
        elif tag == 'li':
            self.slack_message += f'{self.line_break}- '
        elif tag == 'code':
            self.slack_message += '`'
        elif tag == 'a':
            href = [x[1] for x in attrs if x[0] == 'href']
            if len(href) > 0:
                self.slack_message += f'<{href[0]}|'
        else:
            self.ignore_tag = True

    def handle_data(self, data: str):
        """Handles the data within a tag.

        Args:
        data: The data/string within the HTML tag.
        """
        if not self.ignore_tag:
            self.slack_message += data \
                .replace('&', '&amp;') \
                .replace('<', '&lt;') \
                .replace('>', '&gt;')

    def handle_endtag(self, tag: str):
        """Called when the closing of a tag is encountered.

        Args:
            tag: Lowercase name of the HTML tag.  E.G. `br` or `i`.
        """
        if tag in ['i', 'em']:
            self.slack_message += '_'
        elif tag in ['b', 'strong']:
            self.slack_message += '*'
        elif tag == 'strike':
            self.slack_message += '~'
        elif tag == 'p':
            self.slack_message += self.line_break
        elif tag == 'code':
            self.slack_message += '`'
        elif tag == 'a':
            self.slack_message += '>'

        self.ignore_tag = False

    def parse(self, html_string: str) -> str:
        """Parses a given HTML string and applies simple formatting.

        Args:
        html_string: The HTML string to convert to Slack mrkdwn.

        Returns:
            A formatted Slack mrkdwn string.
        """
        self.feed(html_string)
        return re.sub(
            r'^(\n)+',  # Remove the leading line breaks
            '',
            ' '.join(self.slack_message.split()).replace(self.line_break, '\n')
        )


class WebhookResponse:
    def __init__(
            self,
            *,
            status_code: int,
            body: str,
    ):
        self.status_code = status_code
        self.body = body


class TimeoutError(Exception):
    """Exception raised for timeout errors."""

    def __init__(self, message="Timeout occurred when trying to send message to Slack."):
        self.message = message
        super().__init__(self.message)


class CommunicationError(Exception):
    """Exception raised for communication errors."""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)


class SlackWebhook():
    def __init__(self,
                 url: str,
                 timeout: Optional[int] = 15,
                 headers: Optional[Dict[str, str]] = None
                 ):
        """ Class to send messages to a provided Slack webhook URL.
        You can read more about Slack's Incoming Webhooks here:
        https://api.slack.com/messaging/webhooks

        Args:
            url: The webhook URL to send a message to.
            timeout: Number of seconds before the request will time out.
            headers: Request headers to append only for this request
        """
        self.url = url
        self.headers = headers if headers else {"Content-Type": "application/json;charset=utf-8", }
        self.timeout = timeout

    def send(self, *,
             message: str,
             attachments: Optional[Sequence[Dict[str, Any]]] = None,
             blocks: Optional[Sequence[Dict[str, Any]]] = None,
             ) -> Optional[WebhookResponse]:
        """Sends a message to the webhook URL.

        Args:
            message: Plain text string to send to Slack.
            attachments: A collection of attachments
            blocks: A collection of Block Kit UI components

        Returns:
            Webhook response
        """
        payload = {
            'text': message,
            "attachments": attachments,
            "blocks": blocks,
        }
        Logger.debug(f"Sending a request - url: {self.url}, payload: {payload}, headers: {self.headers}")

        http_resp: Optional[Response] = None
        try:
            http_resp = requests.post(self.url,
                                      headers=self.headers,
                                      json=payload,
                                      timeout=self.timeout
                                      )
            http_resp.raise_for_status()
        except requests.Timeout:
            Logger.error('Timeout occurred when trying to send message to Slack.')
            raise TimeoutError('Timeout occurred when trying to send message to Slack.')
        except requests.RequestException as e:
            Logger.error(f'Error occurred when communicating with Slack: {e}.')
            raise CommunicationError(f'Error occurred when communicating with Slack: {e}.')
        else:
            Logger.debug('Successfully sent message to Slack.')

        response_body: str = http_resp.text
        resp = WebhookResponse(
            status_code=http_resp.status_code,
            body=response_body,
        )
        return resp


class SlackBot:
    def __init__(self,
                 token: str,
                 timeout: Optional[int] = 15,
                 ):
        """
        A SlackBot Client allows apps to communicate with Slack Platform
        Args:
            token (str): A string specifying an `xoxp-*` or `xoxb-*` token.
        """
        self.headers = {'Authorization': 'Bearer ' + token, 'Content-type': 'application/x-www-form-urlencoded'}
        self.token = token
        self.timeout = timeout

    def get_latest_n_messages(
            self,
            channel_id: str,
            limit: int = 1
    ) -> Dict[str, Any]:
        """ List latest N messages of a channel
        https://slack.com/api/conversations.history
        Args:
            channel_id: ID of channel that the message send to
            limit: The maximum number of items to return
        """
        api_endpoint = "https://slack.com/api/conversations.history"
        payload = {
            "channel": channel_id,
            "limit": limit,  # Limit to one message
        }
        response = requests.get(api_endpoint, params=payload, headers=self.headers, timeout=self.timeout)
        response.raise_for_status()
        return response.json()

    def reply_latest_message(
            self,
            channel_id: str,
            message: Optional[str] = None
    ) -> bool:
        """ Reply a thread to a latest message
        https://slack.com/api/chat.postMessage
        Args:
            channel_id: ID of channel that the message send to
            message: Plain text string to send to Slack.
        Returns:
            Boolean value
        """
        latest_messages = self.get_latest_n_messages(channel_id, limit=1)
        if not latest_messages.get('messages'):
            return False
        parent_message_timestamp = latest_messages['messages'][0]['ts']
        api_endpoint = "https://slack.com/api/chat.postMessage"
        payload = {
            "text": message,
            "channel": channel_id,
            "thread_ts": parent_message_timestamp,  # Limit to one message
        }
        response = requests.post(api_endpoint, params=payload, headers=self.headers, timeout=self.timeout)
        response_data = response.json()
        Logger.debug(f"Sending a request - url: {api_endpoint}, payload: {payload}, response: {response_data}")
        return response_data.get('ok', False)

    def send_message_to_channels(self, channels: List[str], message: str) -> Dict[str, Tuple[bool, str]]:
        """Send a message to multiple channels.
        Args:
            channels: A list of channel ID
            message: Plain text string to send to Slack.
        Returns:
            A dictionary mapping channel IDs to a tuple of success status and error message (if any).
        """
        results: Dict[str, Tuple[bool, str]] = {}
        for channel_id in channels:
            success, error = self.send_message(channel_id, message)
            results[channel_id] = (success, error)
            Logger.debug(results)
        return results

    def send_message(self, channel_id: str, message: str) -> Tuple[bool, str]:
        """Send a message to a specific channel.
        Args:
            channel_id: The ID of the channel to send the message to.
            message: Plain text string to send to Slack.
        Returns:
            A tuple containing the success status (bool) and the error message (str), if any.
        """
        api_endpoint = "https://slack.com/api/chat.postMessage"
        payload = {
            "text": message,
            "channel": channel_id,
        }
        response = requests.post(api_endpoint, params=payload, headers=self.headers, timeout=self.timeout)
        response_data = response.json()
        Logger.debug(f"Sending a request - url: {api_endpoint}, payload: {payload}, response: {response_data}")
        if not response_data.get('ok'):
            error_message = response_data.get('error', 'Unknown error')
            Logger.error(f"Failed to send message to channel {channel_id}. Error: {error_message}")
            return False, error_message

        return True, ""
