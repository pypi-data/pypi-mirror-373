"""
Tests for Ray client log streaming functionality.
"""

import queue as queue_module
from unittest.mock import AsyncMock, Mock, patch

import pytest
import requests

from synapse_sdk.clients.agent.ray import RayClientMixin
from synapse_sdk.clients.exceptions import ClientError


class RayClientForTesting(RayClientMixin):
    """Test implementation of RayClientMixin for testing."""

    def __init__(self, base_url='http://test.synapse.local'):
        super().__init__(base_url)
        self.agent_token = 'test-agent-token'

    def _get_headers(self):
        return {'Authorization': 'Bearer test-token'}


@pytest.fixture
def ray_client():
    """Create test Ray client."""
    return RayClientForTesting()


@pytest.fixture
def mock_websocket():
    """Mock WebSocket connection."""
    with patch('websockets.connect') as mock_connect:
        mock_websocket = AsyncMock()
        mock_websocket.__aenter__ = AsyncMock(return_value=mock_websocket)
        mock_websocket.__aexit__ = AsyncMock(return_value=None)
        mock_connect.return_value = mock_websocket
        yield mock_websocket


@pytest.fixture
def mock_http_response():
    """Mock HTTP streaming response."""
    mock_response = Mock(spec=requests.Response)
    mock_response.status_code = 200
    mock_response.raise_for_status.return_value = None
    mock_response.iter_lines.return_value = iter(['line1', 'line2', 'line3'])
    mock_response.close.return_value = None
    return mock_response


class TestRayClientLogTailing:
    """Test cases for Ray client log tailing functionality."""

    def test_tail_job_logs_invalid_protocol(self, ray_client):
        """Test tail_job_logs with invalid protocol."""
        with pytest.raises(ClientError) as exc_info:
            list(ray_client.tail_job_logs('job-123', protocol='invalid'))

        assert exc_info.value.status == 400
        assert 'Unsupported protocol' in str(exc_info.value)

    def test_tail_job_logs_invalid_job_pk(self, ray_client):
        """Test tail_job_logs with invalid job PK."""
        with pytest.raises(ClientError) as exc_info:
            list(ray_client.tail_job_logs(''))

        assert exc_info.value.status == 400
        assert 'ID cannot be empty' in str(exc_info.value)

    def test_tail_job_logs_invalid_timeout(self, ray_client):
        """Test tail_job_logs with invalid timeout."""
        with pytest.raises(ClientError) as exc_info:
            list(ray_client.tail_job_logs('job-123', stream_timeout=-1))

        assert exc_info.value.status == 400
        assert 'positive number' in str(exc_info.value)

    def test_tail_job_logs_excessive_timeout(self, ray_client):
        """Test tail_job_logs with excessive timeout."""
        with pytest.raises(ClientError) as exc_info:
            list(ray_client.tail_job_logs('job-123', stream_timeout=500))

        assert exc_info.value.status == 400
        assert 'exceed 300 seconds' in str(exc_info.value)

    def test_tail_job_logs_stream_protocol(self, ray_client, mock_http_response):
        """Test tail_job_logs with stream protocol."""
        with patch.object(ray_client.requests_session, 'get', return_value=mock_http_response):
            logs = list(ray_client.tail_job_logs('job-123', protocol='stream'))

        assert logs == ['line1\n', 'line2\n', 'line3\n']

    @patch('synapse_sdk.utils.network.check_library_available')
    def test_websocket_tail_job_logs_no_websockets(self, mock_check, ray_client):
        """Test WebSocket tailing when websockets library is not available."""
        mock_check.return_value = False

        with pytest.raises(ClientError) as exc_info:
            list(ray_client.websocket_tail_job_logs('job-123'))

        assert exc_info.value.status == 500
        assert 'websockets library not available' in str(exc_info.value)

    @patch('synapse_sdk.utils.network.check_library_available')
    def test_websocket_tail_job_logs_success(self, mock_check, ray_client):
        """Test successful WebSocket log tailing."""
        mock_check.return_value = True

        # Mock the queue module and queue behavior
        with patch('synapse_sdk.utils.network.queue_module') as mock_queue_module:
            mock_message_queue = Mock()
            mock_exception_queue = Mock()

            # Set up queue creation
            def queue_side_effect(*args, **kwargs):
                if 'maxsize' in kwargs and kwargs['maxsize'] == 1000:
                    return mock_message_queue
                elif 'maxsize' in kwargs and kwargs['maxsize'] == 10:
                    return mock_exception_queue
                return Mock()

            mock_queue_module.Queue.side_effect = queue_side_effect
            mock_queue_module.Empty = queue_module.Empty

            # Mock message queue behavior - return a few messages then end signal
            mock_message_queue.get.side_effect = ['message1\n', 'message2\n', None]
            mock_exception_queue.get_nowait.side_effect = queue_module.Empty()

            with patch.object(ray_client._thread_pool, 'submit') as mock_submit:
                mock_future = Mock()
                mock_future.done.side_effect = [False, False, True]  # Done after 3 calls
                mock_future.result.return_value = None  # No exception
                mock_future.cancel.return_value = None
                mock_submit.return_value = mock_future

                logs = list(ray_client.websocket_tail_job_logs('job-123'))

        assert logs == ['message1\n', 'message2\n']

    def test_stream_tail_job_logs_success(self, ray_client, mock_http_response):
        """Test successful HTTP stream log tailing."""
        with patch.object(ray_client.requests_session, 'get', return_value=mock_http_response):
            logs = list(ray_client.stream_tail_job_logs('job-123'))

        assert logs == ['line1\n', 'line2\n', 'line3\n']

    def test_stream_tail_job_logs_connection_error(self, ray_client):
        """Test HTTP stream tailing with connection error."""
        with patch.object(
            ray_client.requests_session, 'get', side_effect=requests.exceptions.ConnectionError('Connection refused')
        ):
            with pytest.raises(ClientError) as exc_info:
                list(ray_client.stream_tail_job_logs('job-123'))

            assert exc_info.value.status == 503
            assert 'connection refused' in str(exc_info.value).lower()

    def test_stream_tail_job_logs_timeout_error(self, ray_client):
        """Test HTTP stream tailing with timeout error."""
        with patch.object(
            ray_client.requests_session, 'get', side_effect=requests.exceptions.ConnectTimeout('Timeout')
        ):
            with pytest.raises(ClientError) as exc_info:
                list(ray_client.stream_tail_job_logs('job-123'))

            assert exc_info.value.status == 408

    def test_stream_tail_job_logs_http_error(self, ray_client):
        """Test HTTP stream tailing with HTTP error."""
        mock_response = Mock()
        mock_response.status_code = 404
        http_error = requests.exceptions.HTTPError()
        http_error.response = mock_response

        with patch.object(ray_client.requests_session, 'get', side_effect=http_error):
            with pytest.raises(ClientError) as exc_info:
                list(ray_client.stream_tail_job_logs('job-123'))

            assert exc_info.value.status == 404

    def test_stream_tail_job_logs_line_limit_exceeded(self, ray_client):
        """Test HTTP stream tailing with line limit exceeded."""
        # Create a response with too many lines
        many_lines = [f'line{i}' for i in range(60000)]  # Exceeds default limit of 50000
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = iter(many_lines)
        mock_response.close.return_value = None

        with patch.object(ray_client.requests_session, 'get', return_value=mock_response):
            with pytest.raises(ClientError) as exc_info:
                list(ray_client.stream_tail_job_logs('job-123'))

            assert exc_info.value.status == 429
            assert 'Line limit exceeded' in str(exc_info.value)

    def test_stream_tail_job_logs_size_limit_exceeded(self, ray_client):
        """Test HTTP stream tailing with size limit exceeded."""
        # Create a response with large lines
        large_line = 'x' * (1024 * 1024)  # 1MB line
        large_lines = [large_line] * 60  # 60MB total, exceeds 50MB limit
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = iter(large_lines)
        mock_response.close.return_value = None

        with patch.object(ray_client.requests_session, 'get', return_value=mock_response):
            with pytest.raises(ClientError) as exc_info:
                list(ray_client.stream_tail_job_logs('job-123'))

            assert exc_info.value.status == 429
            assert 'Size limit exceeded' in str(exc_info.value)

    def test_stream_tail_job_logs_oversized_line_filtered(self, ray_client):
        """Test HTTP stream tailing filters out oversized lines."""
        # Mix normal and oversized lines
        lines = ['normal_line', 'x' * 20000, 'another_normal_line']  # Middle line > 10KB
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.return_value = iter(lines)
        mock_response.close.return_value = None

        with patch.object(ray_client.requests_session, 'get', return_value=mock_response):
            logs = list(ray_client.stream_tail_job_logs('job-123'))

        # Only normal lines should be included
        assert logs == ['normal_line\n', 'another_normal_line\n']

    def test_stream_tail_job_logs_resource_cleanup(self, ray_client):
        """Test that HTTP response is properly closed even on error."""
        mock_response = Mock(spec=requests.Response)
        mock_response.status_code = 200
        mock_response.raise_for_status.return_value = None
        mock_response.iter_lines.side_effect = Exception('Test error')
        mock_response.close.return_value = None

        with patch.object(ray_client.requests_session, 'get', return_value=mock_response):
            with pytest.raises(ClientError):
                list(ray_client.stream_tail_job_logs('job-123'))

        # Verify response.close() was called
        mock_response.close.assert_called_once()


class TestRayClientURLConstruction:
    """Test URL construction in Ray client methods."""

    def test_websocket_tail_job_logs_url_construction(self, ray_client):
        """Test that websocket_tail_job_logs constructs URLs with trailing slash."""
        with patch('synapse_sdk.utils.network.check_library_available', return_value=False):
            try:
                list(ray_client.websocket_tail_job_logs('test-job'))
                pytest.fail('Expected ClientError')
            except ClientError as e:
                assert 'websockets library not available' in str(e)

        # Verify the URL would be constructed correctly by checking _get_url call
        with patch.object(
            ray_client, '_get_url', return_value='http://test.synapse.local/ray/jobs/test-job/logs/ws/'
        ) as mock_get_url:
            with patch('synapse_sdk.utils.network.check_library_available', return_value=False):
                try:
                    list(ray_client.websocket_tail_job_logs('test-job'))
                except ClientError:
                    pass
            mock_get_url.assert_called_with('ray/jobs/test-job/logs/ws/', trailing_slash=True)

    def test_stream_tail_job_logs_url_construction(self, ray_client, mock_http_response):
        """Test that stream_tail_job_logs constructs URLs with trailing slash."""
        with patch.object(
            ray_client, '_get_url', return_value='http://test.synapse.local/ray/jobs/test-job/logs/stream/'
        ) as mock_get_url:
            with patch.object(ray_client.requests_session, 'get', return_value=mock_http_response):
                list(ray_client.stream_tail_job_logs('test-job'))
            mock_get_url.assert_called_with('ray/jobs/test-job/logs/stream/', trailing_slash=True)


class TestRayClientValidation:
    """Test validation logic in Ray client methods."""

    def test_job_pk_validation_empty(self, ray_client):
        """Test job PK validation with empty value."""
        with pytest.raises(ClientError) as exc_info:
            ray_client.websocket_tail_job_logs('')

        assert exc_info.value.status == 400
        assert 'job ID cannot be empty' in str(exc_info.value)

    def test_job_pk_validation_invalid_characters(self, ray_client):
        """Test job PK validation with invalid characters."""
        with pytest.raises(ClientError) as exc_info:
            ray_client.websocket_tail_job_logs('job/../malicious')

        assert exc_info.value.status == 400
        assert 'Invalid job ID format' in str(exc_info.value)

    def test_job_pk_validation_too_long(self, ray_client):
        """Test job PK validation with overly long value."""
        long_pk = 'a' * 150  # Exceeds 100 character limit
        with pytest.raises(ClientError) as exc_info:
            ray_client.websocket_tail_job_logs(long_pk)

        assert exc_info.value.status == 400
        assert 'job ID too long' in str(exc_info.value)

    def test_job_pk_validation_valid_formats(self, ray_client):
        """Test job PK validation with valid formats."""
        valid_pks = [
            'job-123',
            'job_456',
            'abc123',
            'JOB-UUID-123-456',
            '12345',
        ]

        for pk in valid_pks:
            # Should not raise validation error
            with patch('synapse_sdk.utils.network.check_library_available', return_value=False):
                try:
                    list(ray_client.websocket_tail_job_logs(pk))
                    pytest.fail(f'Expected ClientError for pk {pk}')
                except ClientError as e:
                    # Should fail on websockets availability, not validation
                    assert 'websockets library not available' in str(e)


@pytest.mark.integration
class TestRayClientIntegration:
    """Integration tests for Ray client (require actual services)."""

    @pytest.mark.skip(reason='Requires actual Ray service')
    def test_real_websocket_connection(self, ray_client):
        """Test actual WebSocket connection to Ray service."""
        # This would test against a real Ray cluster
        pass

    @pytest.mark.skip(reason='Requires actual Ray service')
    def test_real_http_stream_connection(self, ray_client):
        """Test actual HTTP stream connection to Ray service."""
        # This would test against a real Ray cluster
        pass


if __name__ == '__main__':
    pytest.main([__file__])
