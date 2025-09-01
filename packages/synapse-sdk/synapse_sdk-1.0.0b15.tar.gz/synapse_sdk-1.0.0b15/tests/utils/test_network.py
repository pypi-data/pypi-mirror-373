"""
Tests for network utilities module.
"""

import queue as queue_module
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

import pytest
import requests

from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.utils.network import (
    HTTPStreamManager,
    StreamLimits,
    WebSocketStreamManager,
    check_library_available,
    http_to_websocket_url,
    sanitize_error_message,
    validate_resource_id,
    validate_timeout,
)


class TestValidationFunctions:
    """Test validation utility functions."""

    def test_validate_resource_id_valid(self):
        """Test resource ID validation with valid inputs."""
        valid_ids = [
            'abc123',
            'job-456',
            'user_789',
            'RESOURCE-UUID-123-456',
            '12345',
            'a',
            'A-B_C-123',
        ]

        for resource_id in valid_ids:
            result = validate_resource_id(resource_id, 'test')
            assert result == str(resource_id)

    def test_validate_resource_id_empty(self):
        """Test resource ID validation with empty input."""
        with pytest.raises(ClientError) as exc_info:
            validate_resource_id('', 'job')

        assert exc_info.value.status == 400
        assert 'job ID cannot be empty' in str(exc_info.value)

    def test_validate_resource_id_none(self):
        """Test resource ID validation with None input."""
        with pytest.raises(ClientError) as exc_info:
            validate_resource_id(None, 'user')

        assert exc_info.value.status == 400
        assert 'user ID cannot be empty' in str(exc_info.value)

    def test_validate_resource_id_invalid_characters(self):
        """Test resource ID validation with invalid characters."""
        invalid_ids = [
            'job/../malicious',
            'user@domain.com',
            'resource with spaces',
            'id\nwith\nnewlines',
            'id\twith\ttabs',
            'id"with"quotes',
            "id'with'quotes",
            'id\\with\\backslashes',
            'id/with/slashes',
        ]

        for resource_id in invalid_ids:
            with pytest.raises(ClientError) as exc_info:
                validate_resource_id(resource_id, 'test')

            assert exc_info.value.status == 400
            assert 'Invalid test ID format' in str(exc_info.value)

    def test_validate_resource_id_too_long(self):
        """Test resource ID validation with overly long input."""
        long_id = 'a' * 150  # Exceeds 100 character limit
        with pytest.raises(ClientError) as exc_info:
            validate_resource_id(long_id, 'resource')

        assert exc_info.value.status == 400
        assert 'resource ID too long' in str(exc_info.value)

    def test_validate_timeout_valid(self):
        """Test timeout validation with valid inputs."""
        valid_timeouts = [1, 5, 30, 60, 120, 300, 1.5, 2.7]

        for timeout in valid_timeouts:
            result = validate_timeout(timeout)
            assert result == float(timeout)

    def test_validate_timeout_invalid_type(self):
        """Test timeout validation with invalid types."""
        invalid_timeouts = ['30', None, [], {}, object()]

        for timeout in invalid_timeouts:
            with pytest.raises(ClientError) as exc_info:
                validate_timeout(timeout)

            assert exc_info.value.status == 400
            assert 'positive number' in str(exc_info.value)

    def test_validate_timeout_negative(self):
        """Test timeout validation with negative values."""
        negative_timeouts = [-1, -0.1, -100]

        for timeout in negative_timeouts:
            with pytest.raises(ClientError) as exc_info:
                validate_timeout(timeout)

            assert exc_info.value.status == 400
            assert 'positive number' in str(exc_info.value)

    def test_validate_timeout_zero(self):
        """Test timeout validation with zero."""
        with pytest.raises(ClientError) as exc_info:
            validate_timeout(0)

        assert exc_info.value.status == 400
        assert 'positive number' in str(exc_info.value)

    def test_validate_timeout_excessive(self):
        """Test timeout validation with excessive values."""
        excessive_timeouts = [301, 500, 1000]

        for timeout in excessive_timeouts:
            with pytest.raises(ClientError) as exc_info:
                validate_timeout(timeout)

            assert exc_info.value.status == 400
            assert 'exceed 300 seconds' in str(exc_info.value)

    def test_validate_timeout_custom_max(self):
        """Test timeout validation with custom maximum."""
        result = validate_timeout(50, max_timeout=60)
        assert result == 50.0

        with pytest.raises(ClientError) as exc_info:
            validate_timeout(70, max_timeout=60)

        assert exc_info.value.status == 400
        assert 'exceed 60 seconds' in str(exc_info.value)


class TestURLConversion:
    """Test URL conversion utilities."""

    def test_http_to_websocket_url_http(self):
        """Test HTTP to WebSocket URL conversion."""
        result = http_to_websocket_url('http://example.com/path')
        assert result == 'ws://example.com/path'

    def test_http_to_websocket_url_https(self):
        """Test HTTPS to WebSocket URL conversion."""
        result = http_to_websocket_url('https://example.com/path')
        assert result == 'wss://example.com/path'

    def test_http_to_websocket_url_with_query(self):
        """Test URL conversion with query parameters."""
        result = http_to_websocket_url('https://example.com/path?param=value')
        assert result == 'wss://example.com/path?param=value'

    def test_http_to_websocket_url_with_fragment(self):
        """Test URL conversion with fragment."""
        result = http_to_websocket_url('https://example.com/path#fragment')
        assert result == 'wss://example.com/path#fragment'

    def test_http_to_websocket_url_invalid_scheme(self):
        """Test URL conversion with invalid scheme."""
        with pytest.raises(ClientError) as exc_info:
            http_to_websocket_url('ftp://example.com/path')

        assert exc_info.value.status == 400
        assert 'Invalid URL scheme' in str(exc_info.value)

    def test_http_to_websocket_url_malformed(self):
        """Test URL conversion with malformed URL."""
        with pytest.raises(ClientError) as exc_info:
            http_to_websocket_url('not-a-url')

        assert exc_info.value.status == 400
        assert 'Invalid URL format' in str(exc_info.value)


class TestErrorSanitization:
    """Test error message sanitization."""

    def test_sanitize_error_message_basic(self):
        """Test basic error message sanitization."""
        result = sanitize_error_message('Simple error message')
        assert result == 'Simple error message'

    def test_sanitize_error_message_with_context(self):
        """Test error message sanitization with context."""
        result = sanitize_error_message('Error occurred', 'job 123')
        assert result == 'job 123: Error occurred'

    def test_sanitize_error_message_with_secrets(self):
        """Test error message sanitization removes secrets."""
        message = 'Connection failed with token="secret123" and password="admin123"'
        result = sanitize_error_message(message)
        expected = 'Connection failed with token="[REDACTED]" and password="[REDACTED]"'
        assert result == expected

    def test_sanitize_error_message_length_limit(self):
        """Test error message sanitization respects length limit."""
        long_message = 'x' * 200
        result = sanitize_error_message(long_message)
        assert len(result) <= 100

    def test_sanitize_error_message_mixed_quotes(self):
        """Test error message sanitization with mixed quotes."""
        message = 'Error: token="secret" and key=\'another_secret\''
        result = sanitize_error_message(message)
        expected = 'Error: token="[REDACTED]" and key="[REDACTED]"'
        assert result == expected


class TestLibraryAvailability:
    """Test library availability checking."""

    def test_check_library_available_existing(self):
        """Test checking for existing library."""
        result = check_library_available('sys')  # Built-in module
        assert result is True

    def test_check_library_available_nonexistent(self):
        """Test checking for non-existent library."""
        result = check_library_available('nonexistent_library_12345')
        assert result is False

    def test_check_library_available_optional(self):
        """Test checking for optional libraries."""
        # These may or may not be installed
        libraries = ['websockets', 'asyncio', 'ssl']
        for lib in libraries:
            result = check_library_available(lib)
            assert isinstance(result, bool)


class TestStreamLimits:
    """Test StreamLimits configuration."""

    def test_stream_limits_defaults(self):
        """Test StreamLimits with default values."""
        limits = StreamLimits()
        assert limits.max_messages == 10000
        assert limits.max_lines == 50000
        assert limits.max_bytes == 50 * 1024 * 1024
        assert limits.max_message_size == 10240
        assert limits.queue_size == 1000
        assert limits.exception_queue_size == 10

    def test_stream_limits_custom(self):
        """Test StreamLimits with custom values."""
        limits = StreamLimits(
            max_messages=5000,
            max_lines=25000,
            max_bytes=25 * 1024 * 1024,
            max_message_size=5120,
            queue_size=500,
            exception_queue_size=5,
        )
        assert limits.max_messages == 5000
        assert limits.max_lines == 25000
        assert limits.max_bytes == 25 * 1024 * 1024
        assert limits.max_message_size == 5120
        assert limits.queue_size == 500
        assert limits.exception_queue_size == 5


class TestWebSocketStreamManager:
    """Test WebSocketStreamManager functionality."""

    @pytest.fixture
    def thread_pool(self):
        """Create thread pool for testing."""
        return ThreadPoolExecutor(max_workers=2)

    @pytest.fixture
    def ws_manager(self, thread_pool):
        """Create WebSocket stream manager."""
        return WebSocketStreamManager(thread_pool)

    def test_websocket_manager_initialization(self, thread_pool):
        """Test WebSocket manager initialization."""
        manager = WebSocketStreamManager(thread_pool)
        assert manager.thread_pool is thread_pool
        assert isinstance(manager.limits, StreamLimits)

    def test_websocket_manager_custom_limits(self, thread_pool):
        """Test WebSocket manager with custom limits."""
        limits = StreamLimits(max_messages=1000)
        manager = WebSocketStreamManager(thread_pool, limits)
        assert manager.limits is limits

    @patch('synapse_sdk.utils.network.check_library_available')
    def test_websocket_manager_no_library(self, mock_check, ws_manager):
        """Test WebSocket manager when library is unavailable."""
        mock_check.return_value = False

        with pytest.raises(ClientError) as exc_info:
            list(ws_manager.stream_logs('ws://test.com', {}, 30, 'test'))

        assert exc_info.value.status == 500
        assert 'websockets library not available' in str(exc_info.value)

    @patch('synapse_sdk.utils.network.check_library_available')
    @patch('asyncio.run')
    def test_websocket_manager_stream_logs(self, mock_asyncio_run, mock_check, ws_manager):
        """Test WebSocket manager streaming logs."""
        mock_check.return_value = True

        # Mock the queues and threading
        with patch('queue.Queue') as mock_queue_class:
            mock_message_queue = Mock()
            mock_exception_queue = Mock()
            mock_queue_class.side_effect = [mock_message_queue, mock_exception_queue]

            # Mock queue behavior
            mock_message_queue.get.side_effect = ['msg1\n', 'msg2\n', None]
            mock_exception_queue.get_nowait.side_effect = queue_module.Empty()

            with patch.object(ws_manager.thread_pool, 'submit') as mock_submit:
                mock_future = Mock()
                mock_future.done.return_value = False
                mock_future.cancel.return_value = None
                mock_submit.return_value = mock_future

                # Should get some messages before stopping
                logs = []
                try:
                    for log in ws_manager.stream_logs('ws://test.com', {}, 30, 'test'):
                        logs.append(log)
                        if len(logs) >= 2:  # Stop after getting some logs
                            break
                except Exception:
                    pass  # Expected due to mocking

                # Verify submit was called
                mock_submit.assert_called_once()


class TestHTTPStreamManager:
    """Test HTTPStreamManager functionality."""

    @pytest.fixture
    def requests_session(self):
        """Create mock requests session."""
        return Mock(spec=requests.Session)

    @pytest.fixture
    def http_manager(self, requests_session):
        """Create HTTP stream manager."""
        return HTTPStreamManager(requests_session)

    def test_http_manager_initialization(self, requests_session):
        """Test HTTP manager initialization."""
        manager = HTTPStreamManager(requests_session)
        assert manager.requests_session is requests_session
        assert isinstance(manager.limits, StreamLimits)

    def test_http_manager_custom_limits(self, requests_session):
        """Test HTTP manager with custom limits."""
        limits = StreamLimits(max_lines=1000)
        manager = HTTPStreamManager(requests_session, limits)
        assert manager.limits is limits

    def test_http_manager_stream_logs_success(self, http_manager):
        """Test HTTP manager successful log streaming."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = iter(['line1', 'line2', 'line3'])
        mock_response.close.return_value = None

        http_manager.requests_session.get.return_value = mock_response

        logs = list(http_manager.stream_logs('http://test.com', {}, (5, 30), 'test'))

        assert logs == ['line1\n', 'line2\n', 'line3\n']
        mock_response.close.assert_called_once()

    def test_http_manager_stream_logs_connection_error(self, http_manager):
        """Test HTTP manager with connection error."""
        http_manager.requests_session.get.side_effect = requests.exceptions.ConnectionError('Connection refused')

        with pytest.raises(ClientError) as exc_info:
            list(http_manager.stream_logs('http://test.com', {}, (5, 30), 'test'))

        assert exc_info.value.status == 503
        assert 'connection refused' in str(exc_info.value).lower()

    def test_http_manager_stream_logs_line_limit(self, http_manager):
        """Test HTTP manager with line limit exceeded."""
        # Override limits for this test
        http_manager.limits.max_lines = 2

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = iter(['line1', 'line2', 'line3'])
        mock_response.close.return_value = None

        http_manager.requests_session.get.return_value = mock_response

        with pytest.raises(ClientError) as exc_info:
            list(http_manager.stream_logs('http://test.com', {}, (5, 30), 'test'))

        assert exc_info.value.status == 429
        assert 'Line limit exceeded' in str(exc_info.value)

    def test_http_manager_stream_logs_size_limit(self, http_manager):
        """Test HTTP manager with size limit exceeded."""
        # Override limits for this test
        http_manager.limits.max_bytes = 10  # Very small limit

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = iter(['large_line_content'])
        mock_response.close.return_value = None

        http_manager.requests_session.get.return_value = mock_response

        with pytest.raises(ClientError) as exc_info:
            list(http_manager.stream_logs('http://test.com', {}, (5, 30), 'test'))

        assert exc_info.value.status == 429
        assert 'Size limit exceeded' in str(exc_info.value)

    def test_http_manager_stream_logs_oversized_line_filtered(self, http_manager):
        """Test HTTP manager filters oversized lines."""
        # Override limits for this test
        http_manager.limits.max_message_size = 10

        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        # Mix normal and oversized lines
        mock_response.iter_lines.return_value = iter(['short', 'very_long_line_that_exceeds_limit', 'normal'])
        mock_response.close.return_value = None

        http_manager.requests_session.get.return_value = mock_response

        logs = list(http_manager.stream_logs('http://test.com', {}, (5, 30), 'test'))

        # Only normal-sized lines should be included
        assert logs == ['short\n', 'normal\n']

    def test_http_manager_resource_cleanup_on_error(self, http_manager):
        """Test HTTP manager cleans up resources on error."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.side_effect = Exception('Test error')
        mock_response.close.return_value = None

        http_manager.requests_session.get.return_value = mock_response

        with pytest.raises(ClientError):
            list(http_manager.stream_logs('http://test.com', {}, (5, 30), 'test'))

        # Verify response was closed
        mock_response.close.assert_called_once()


if __name__ == '__main__':
    pytest.main([__file__])
