import pytest
from unittest.mock import MagicMock, patch

import queue as std_queue

from liveramp_automation.helpers.grafana_multi_process import (
    GrafanaClient,
    GrafanaAuthenticationError,
    GrafanaAPIError,
    _GrafanaWorker,
)


@pytest.fixture
def client_config():
    return {
        "username": "test@example.com",
        "password": "secret",
        "base_url": "https://test.grafana.net",
        "headless": True,
        "timeout": 30000,
    }


def _setup_process_and_queues(mock_queue, mock_process, res_side_effect):
    """Helper to configure mocked Queue and Process for a client session.

    res_side_effect: list or exception for res_queue.get.side_effect
    """
    cmd_q = MagicMock()
    res_q = MagicMock()
    mock_queue.side_effect = [cmd_q, res_q]

    proc = MagicMock()
    proc.is_alive.return_value = True
    mock_process.return_value = proc

    if isinstance(res_side_effect, list):
        res_q.get.side_effect = res_side_effect
    else:
        res_q.get.side_effect = res_side_effect

    return cmd_q, res_q, proc


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_context_enter_success(mock_queue, mock_process, client_config):
    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[{"status": "ready"}],
    )

    with GrafanaClient(**client_config) as client:
        assert client is not None
        proc.start.assert_called_once()
        # Ensure handshake consumed one get
        assert res_q.get.call_count == 1


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_context_enter_timeout(mock_queue, mock_process, client_config):
    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=std_queue.Empty,
    )

    with pytest.raises(GrafanaAuthenticationError, match="initialize within timeout"):
        with GrafanaClient(**client_config):
            pass

    proc.terminate.assert_called_once()
    proc.join.assert_called()


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_context_enter_error_status(mock_queue, mock_process, client_config):
    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[{"status": "error", "message": "bad"}],
    )

    with pytest.raises(GrafanaAuthenticationError, match="failed to initialize|failed to initialize|Worker failed to initialize"):
        with GrafanaClient(**client_config):
            pass

    proc.join.assert_called()


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_query_loki_success(mock_queue, mock_process, client_config):
    # First call: ready, Second call: success for query
    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[{"status": "ready"}, {"status": "success", "data": {"ok": 1}}],
    )

    payload = {"queries": [], "from": "now-1h", "to": "now"}

    with GrafanaClient(**client_config) as client:
        result = client.query_loki(payload)
        assert result == {"ok": 1}
        # Ensure a command was sent with the right action
        assert cmd_q.put.call_args[0][0]["action"] == "query_loki"


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_query_loki_error(mock_queue, mock_process, client_config):
    # First call: ready, Second call: error for query
    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[{"status": "ready"}, {"status": "error", "message": "boom"}],
    )

    payload = {"queries": [], "from": "now-1h", "to": "now"}

    with GrafanaClient(**client_config) as client:
        with pytest.raises(GrafanaAPIError, match="boom"):

          
          
class TestGrafanaClient:
    """Test cases for GrafanaClient class."""

    @pytest.fixture
    def mock_playwright(self):
        """Mock Playwright components."""
        with patch('liveramp_automation.helpers.grafana.sync_playwright') as mock_playwright:
            mock_p = Mock()
            mock_browser = Mock()
            mock_context = Mock()
            mock_page = Mock()
            
            mock_playwright.return_value.start.return_value = mock_p
            mock_p.chromium.launch.return_value = mock_browser
            mock_browser.new_context.return_value = mock_context
            mock_context.new_page.return_value = mock_page
            
            yield {
                'playwright': mock_playwright,
                'p': mock_p,
                'browser': mock_browser,
                'context': mock_context,
                'page': mock_page
            }

    @pytest.fixture
    def client_config(self):
        """Sample client configuration."""
        return {
            'username': 'test@example.com',
            'password': 'testpass',
            'base_url': 'https://test.grafana.net',
            'headless': True,
            'timeout': 30000
        }
    
    @pytest.fixture
    def initialized_client(self, mock_playwright, client_config):
        """Return a GrafanaClient initialized with mock components."""
        client = GrafanaClient(**client_config)
        client._p = mock_playwright['p']
        client._browser = mock_playwright['browser']
        client._context = mock_playwright['context']
        client._page = mock_playwright['page']
        return client
    
    @pytest.fixture
    def success_response(self):
        """Return a mock successful API response."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status = 200
        mock_response.json.return_value = {"data": {"result": []}}
        return mock_response
    
    @pytest.fixture
    def error_response(self):
        """Return a mock error API response."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"
        return mock_response
    
    def assert_cleanup_called(self, mock_objects):
        """Assert that all cleanup methods were called."""
        mock_objects['page'].close.assert_called_once()
        mock_objects['context'].close.assert_called_once()
        mock_objects['browser'].close.assert_called_once()
        mock_objects['p'].stop.assert_called_once()

    def test_init(self, client_config):
        """Test GrafanaClient initialization."""
        client = GrafanaClient(**client_config)
        
        assert client._username == 'test@example.com'
        assert client._password == 'testpass'
        assert client._base_url == 'https://test.grafana.net'
        assert client._headless is True
        assert client._timeout == 30000
        assert client._login_url == 'https://test.grafana.net/login'
        assert client._api_url == 'https://test.grafana.net/api/ds/query'

    def test_init_with_trailing_slash(self):
        """Test that trailing slashes are properly handled."""
        client = GrafanaClient('user', 'pass', base_url='https://test.grafana.net/')
        assert client._base_url == 'https://test.grafana.net'

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_context_enter_success(self, mock_logger, mock_playwright, client_config):
        """Test successful context manager entry."""
        mock_playwright['page'].wait_for_url.return_value = None
        
        with GrafanaClient(**client_config) as client:
            assert client is not None
            assert client._p is not None
            assert client._browser is not None
            assert client._context is not None
            assert client._page is not None

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_context_enter_failure(self, mock_logger, mock_playwright, client_config):
        """Test context manager entry failure."""
        mock_playwright['p'].chromium.launch.side_effect = Exception("Launch failed")
        
        with pytest.raises(GrafanaAuthenticationError, match="Failed to initialize: Launch failed"):
            with GrafanaClient(**client_config) as client:
                pass

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_context_enter_new_context_failure(self, mock_logger, mock_playwright, client_config):
        """Test context manager entry failure when new_context fails."""
        mock_playwright['browser'].new_context.side_effect = Exception("Context creation failed")
        
        with pytest.raises(GrafanaAuthenticationError, match="Failed to initialize: Context creation failed"):
            with GrafanaClient(**client_config) as client:
                pass

        mock_playwright['browser'].close.assert_called_once()
        mock_playwright['p'].stop.assert_called_once()

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_context_exit(self, mock_logger, mock_playwright, initialized_client):
        """Test context manager exit."""
        mock_playwright['page'].wait_for_url.return_value = None
        
        initialized_client.__exit__(None, None, None)
        
        self.assert_cleanup_called(mock_playwright)

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_cleanup_with_errors(self, mock_logger, mock_playwright, initialized_client):
        """Test cleanup handles errors gracefully."""
        mock_playwright['page'].close.side_effect = Exception("Close failed")
        
        # Should not raise exception
        initialized_client._cleanup()
        mock_logger.warning.assert_called_once()

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_cleanup_multiple_errors(self, mock_logger, mock_playwright, initialized_client):
        """Test cleanup continues after multiple errors."""
        mock_playwright['page'].close.side_effect = Exception("Page close failed")
        mock_playwright['context'].close.side_effect = Exception("Context close failed")
        mock_playwright['browser'].close.side_effect = Exception("Browser close failed")
        mock_playwright['p'].stop.side_effect = Exception("Playwright stop failed")
        
        # Should not raise exception
        initialized_client._cleanup()
        
        assert mock_logger.warning.call_count == 4

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_cleanup_partial_initialization(self, mock_logger, mock_playwright, client_config):
        """Test cleanup with partial initialization."""
        client = GrafanaClient(**client_config)
        client._p = mock_playwright['p']
        client._browser = mock_playwright['browser']
        client._context = mock_playwright['context']
        client._page = None  # Simulate partial initialization

        # Should not raise exception
        client._cleanup()

        mock_playwright['context'].close.assert_called_once()
        mock_playwright['browser'].close.assert_called_once()
        mock_playwright['p'].stop.assert_called_once()

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_context_enter_cleanup_error(self, mock_logger, mock_playwright, client_config):
        """Test that original exception is preserved when cleanup fails in __enter__."""
        original_exception = Exception("Initial setup failed")
        mock_playwright['p'].chromium.launch.side_effect = original_exception
        mock_playwright['page'].close.side_effect = Exception("Cleanup failed")

        with pytest.raises(GrafanaAuthenticationError, match=str(original_exception)):
            with GrafanaClient(**client_config) as client:
                pass

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_cleanup_missing_method(self, mock_logger, mock_playwright, client_config):
        """Test cleanup when a resource is missing its cleanup method."""
        client = GrafanaClient(**client_config)
        # Mock the _page object to not have a close method
        mock_page_without_close = Mock()
        del mock_page_without_close.close
        client._page = mock_page_without_close

        # Call cleanup and assert that it handles the missing method gracefully
        client._cleanup()

        # Assert that the logger's warning method was called
        mock_logger.warning.assert_called_once()

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_authentication_success(self, mock_logger, mock_playwright, client_config):
        """Test successful authentication flow."""
        # Mock successful authentication
        mock_playwright['page'].wait_for_url.return_value = None
        
        client = GrafanaClient(**client_config)
        client._page = mock_playwright['page']
        
        # Should not raise exception
        client._authenticate()

    def test_query_loki_success(self, mock_playwright, initialized_client, success_response):
        """Test successful Loki query."""
        mock_playwright['context'].request.post.return_value = success_response
        
        payload = {"queries": [], "from": "now-1h", "to": "now"}
        result = initialized_client.query_loki(payload)
        
        assert result == {"data": {"result": []}}
        mock_playwright['context'].request.post.assert_called_once()

    def test_query_loki_failure(self, mock_playwright, initialized_client, error_response):
        """Test Loki query failure."""
        mock_playwright['context'].request.post.return_value = error_response
        
        payload = {"queries": [], "from": "now-1h", "to": "now"}
        
        with pytest.raises(GrafanaAPIError, match="API query failed"):
            initialized_client.query_loki(payload)

    def test_query_loki_timestamp_override(self, mock_playwright, initialized_client, success_response):
        """Test that timestamp overrides work correctly."""
        mock_playwright['context'].request.post.return_value = success_response
        
        original_payload = {"queries": [], "from": "original", "to": "original"}
        result = initialized_client.query_loki(
            original_payload, 
            from_timestamp="new_from", 
            to_timestamp="new_to"
        )
        
        # Verify the original payload wasn't modified
        assert original_payload["from"] == "original"
        assert original_payload["to"] == "original"
        
        # Verify the API call used the new timestamps
        call_args = mock_playwright['context'].request.post.call_args
        sent_payload = call_args[1]['data']
        assert "new_from" in sent_payload
        assert "new_to" in sent_payload


    def test_query_loki_non_json_response(self, mock_playwright, client_config):
        """Test handling of non-JSON responses from the Grafana API."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.status = 200
        mock_response.json.side_effect = ValueError("No JSON object could be decoded")

        mock_playwright['context'].request.post.return_value = mock_response

        client = GrafanaClient(**client_config)
        client._context = mock_playwright['context']

        payload = {"queries": [], "from": "now-1h", "to": "now"}

        with pytest.raises(GrafanaAPIError, match="API query failed: No JSON object could be decoded"):
            client.query_loki(payload)

    def test_query_loki_missing_queries_field(self, mock_playwright, client_config):
        """Test Loki query with a malformed payload (missing 'queries' field)."""
        # Mock a failed response from the API
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status = 500
        mock_response.text.return_value = "Internal Server Error"

        mock_playwright['context'].request.post.return_value = mock_response

        client = GrafanaClient(**client_config)
        client._context = mock_playwright['context']

        # Payload missing the 'queries' field
        payload = {"from": "now-1h", "to": "now"}

        with pytest.raises(GrafanaAPIError, match="API query failed"):
            client.query_loki(payload)

    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_context_exit_logs_info_message(self, mock_logger, mock_playwright, initialized_client):
        """Test that __exit__ logs an info message."""
        initialized_client.__exit__(None, None, None)

        mock_logger.info.assert_called_with("Exiting GrafanaClient context. Cleaning up resources.")
        self.assert_cleanup_called(mock_playwright)

    @patch('liveramp_automation.helpers.grafana.GrafanaClient._cleanup')
    @patch('liveramp_automation.helpers.grafana.GrafanaClient._authenticate')
    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_context_enter_authentication_failure(self, mock_logger, mock_authenticate, mock_cleanup, mock_playwright, client_config):
        """Test context manager entry with authentication failure."""
        mock_authenticate.side_effect = Exception("Authentication failed")
        
        with pytest.raises(GrafanaAuthenticationError, match="Failed to initialize: Authentication failed"):
            with GrafanaClient(**client_config) as client:
                pass

        mock_cleanup.assert_called_once()

    @patch('liveramp_automation.helpers.grafana.GrafanaClient._cleanup')
    @patch('liveramp_automation.helpers.grafana.Logger')
    def test_context_exit_with_exception(self, mock_logger, mock_cleanup, mock_playwright, initialized_client):
        """Test context manager exit when an exception occurs in the context body."""
        mock_cleanup.side_effect = None  # Reset side effect
        mock_playwright['page'].wait_for_url.return_value = None
        
        context_exception = Exception("Simulated context exception")

        with pytest.raises(Exception, match="Simulated context exception"):
            with initialized_client:
                raise context_exception

        mock_cleanup.assert_called_once()

    @patch('liveramp_automation.helpers.grafana.GrafanaClient._cleanup')
    def test_exit_does_not_suppress_exception(self, mock_cleanup, mock_playwright, initialized_client):
        """Test that __exit__ doesn't suppress exceptions from the context manager body."""
        with pytest.raises(ValueError, match="Intentional exception"):
            with initialized_client:
                raise ValueError("Intentional exception")

        mock_cleanup.assert_called_once()


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_invoke_timeout(mock_queue, mock_process, client_config):
    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[{"status": "ready"}, std_queue.Empty],
    )

    with GrafanaClient(**client_config) as client:
        with pytest.raises(GrafanaAPIError, match="timed out"):
            client.query_loki({"queries": [], "from": "now-1h", "to": "now"}, timeout=0.01)


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_dynamic_method_proxy_success(mock_queue, mock_process, client_config):
    # Add a dummy public method to the worker class
    def dummy(self, x: int, y: int) -> int:  # pragma: no cover - executed in worker normally
        return x + y

    setattr(_GrafanaWorker, "dummy", dummy)

    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[{"status": "ready"}, {"status": "success", "data": 7}],
    )

    with GrafanaClient(**client_config) as client:
        out = client.dummy(3, 4)
        assert out == 7
        # Confirm the action name was routed dynamically
        assert cmd_q.put.call_args[0][0]["action"] == "dummy"


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_dynamic_method_proxy_attribute_guards(mock_queue, mock_process, client_config):
    # Private method should not be exposed
    def _hidden(self):  # pragma: no cover
        return True
    setattr(_GrafanaWorker, "_hidden", _hidden)

    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[{"status": "ready"}],
    )

    with GrafanaClient(**client_config) as client:
        with pytest.raises(AttributeError):
            _ = client._hidden  # noqa: F841
        with pytest.raises(AttributeError):
            _ = client.this_method_does_not_exist  # noqa: F841


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_context_exit_cleanup(mock_queue, mock_process, client_config):
    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[{"status": "ready"}],
    )

    client = GrafanaClient(**client_config)
    client.__enter__()
    client.__exit__(None, None, None)

    # Ensure an exit command was sent
    assert any(call[0][0].get("action") == "exit" for call in cmd_q.put.call_args_list)
    proc.join.assert_called()


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_exit_terminates_if_still_alive(mock_queue, mock_process, client_config):
    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[{"status": "ready"}],
    )

    # First is_alive() -> True (enter path), Second is_alive() -> True (post-join)
    proc.is_alive.side_effect = [True, True]

    client = GrafanaClient(**client_config)
    client.__enter__()
    client.__exit__(None, None, None)

    proc.terminate.assert_called_once()


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_process_not_running_raises_on_call(mock_queue, mock_process, client_config):
    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[{"status": "ready"}],
    )

    with GrafanaClient(**client_config) as client:
        # Simulate worker death
        proc.is_alive.return_value = False
        with pytest.raises(GrafanaAPIError, match="not running"):
            client.query_loki({"queries": [], "from": "now-1h", "to": "now"})


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_multiple_calls_sequential_success(mock_queue, mock_process, client_config):
    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[
            {"status": "ready"},
            {"status": "success", "data": 1},
            {"status": "success", "data": 2},
        ],
    )

    with GrafanaClient(**client_config) as client:
        a = client.query_loki({"queries": [], "from": "now-1h", "to": "now"})
        b = client.query_loki({"queries": [], "from": "now-1h", "to": "now"})
        assert (a, b) == (1, 2)
        assert cmd_q.put.call_count == 2


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_kwonly_signature_binding(mock_queue, mock_process, client_config):
    def dummy_kw(self, *, a: int, b: int) -> int:  # pragma: no cover
        return a + b

    setattr(_GrafanaWorker, "dummy_kw", dummy_kw)

    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[{"status": "ready"}, {"status": "success", "data": 3}],
    )

    with GrafanaClient(**client_config) as client:
        out = client.dummy_kw(a=1, b=2)
        assert out == 3
        with pytest.raises(TypeError):
            client.dummy_kw(1, 2)


@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Process")
@patch("liveramp_automation.helpers.grafana_multi_process.multiprocessing.Queue")
def test_queue_closed_on_exit(mock_queue, mock_process, client_config):
    cmd_q, res_q, proc = _setup_process_and_queues(
        mock_queue,
        mock_process,
        res_side_effect=[{"status": "ready"}],
    )

    client = GrafanaClient(**client_config)
    client.__enter__()
    client.__exit__(None, None, None)

    for q in (cmd_q, res_q):
        assert q.close.called
        assert q.join_thread.called

