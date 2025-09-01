import weakref
from concurrent.futures import ThreadPoolExecutor

from synapse_sdk.clients.base import BaseClient
from synapse_sdk.clients.exceptions import ClientError
from synapse_sdk.utils.network import (
    HTTPStreamManager,
    StreamLimits,
    WebSocketStreamManager,
    http_to_websocket_url,
    sanitize_error_message,
    validate_resource_id,
    validate_timeout,
)


class RayClientMixin(BaseClient):
    """Mixin class providing Ray cluster management and monitoring functionality.

    This mixin extends BaseClient with Ray-specific operations for interacting with
    Apache Ray distributed computing clusters. It provides comprehensive job management,
    node monitoring, task tracking, and Ray Serve application control capabilities.

    Key Features:
        - Job lifecycle management (list, get, monitor)
        - Real-time log streaming via WebSocket and HTTP protocols
        - Node and task monitoring
        - Ray Serve application deployment and management
        - Robust error handling with input validation
        - Resource management with automatic cleanup

    Streaming Capabilities:
        - WebSocket streaming for real-time log tailing
        - HTTP streaming as fallback protocol
        - Configurable timeouts and stream limits
        - Automatic protocol validation and error recovery

    Resource Management:
        - Thread pool for concurrent operations (5 workers)
        - WeakSet for tracking active connections
        - Automatic cleanup on object destruction
        - Stream limits to prevent resource exhaustion

    Usage Examples:
        Basic job operations:
            >>> client = RayClient(base_url="http://ray-head:8265")
            >>> jobs = client.list_jobs()
            >>> job = client.get_job('job-12345')

        Real-time log streaming:
            >>> # WebSocket streaming (preferred)
            >>> for log_line in client.tail_job_logs('job-12345', protocol='websocket'):
            ...     print(log_line)

            >>> # HTTP streaming (fallback)
            >>> for log_line in client.tail_job_logs('job-12345', protocol='stream'):
            ...     print(log_line)

        Node and task monitoring:
            >>> nodes = client.list_nodes()
            >>> tasks = client.list_tasks()
            >>> node_details = client.get_node('node-id')

        Ray Serve management:
            >>> apps = client.list_serve_applications()
            >>> client.delete_serve_application('app-id')

    Note:
        This class is designed as a mixin and should be combined with other
        client classes that provide authentication and base functionality.
        It requires the BaseClient foundation for HTTP operations.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._thread_pool = ThreadPoolExecutor(max_workers=5, thread_name_prefix='ray_client_')
        self._active_connections = weakref.WeakSet()

        # Initialize stream managers
        stream_limits = StreamLimits()
        self._websocket_manager = WebSocketStreamManager(self._thread_pool, stream_limits)
        self._http_manager = HTTPStreamManager(self.requests_session, stream_limits)

    def get_job(self, pk):
        path = f'jobs/{pk}/'
        return self._get(path)

    def list_jobs(self):
        path = 'jobs/'
        return self._get(path)

    def list_job_logs(self, pk):
        path = f'jobs/{pk}/logs/'
        return self._get(path)

    def websocket_tail_job_logs(self, pk, stream_timeout=10):
        """Stream job logs in real-time using WebSocket protocol.

        Establishes a WebSocket connection to stream job logs as they are generated.
        This method provides the lowest latency for real-time log monitoring and is
        the preferred protocol when available.

        Args:
            pk (str): Job primary key or identifier. Must be alphanumeric with
                     optional hyphens/underscores, max 100 characters.
            stream_timeout (float, optional): Maximum time in seconds to wait for
                                            log data. Defaults to 10. Must be positive
                                            and cannot exceed 300 seconds.

        Returns:
            Generator[str, None, None]: A generator yielding log lines as strings.
                                      Each line includes a newline character.

        Raises:
            ClientError:
                - 400: If long polling is enabled (incompatible)
                - 400: If pk is empty, contains invalid characters, or too long
                - 400: If stream_timeout is not positive or exceeds maximum
                - 500: If WebSocket library is unavailable
                - 503: If connection to Ray cluster fails
                - 408: If connection timeout occurs
                - 429: If stream limits are exceeded (lines, size, messages)

        Usage:
            >>> # Basic log streaming
            >>> for log_line in client.websocket_tail_job_logs('job-12345'):
            ...     print(log_line.strip())

            >>> # With custom timeout
            >>> for log_line in client.websocket_tail_job_logs('job-12345', stream_timeout=30):
            ...     if 'ERROR' in log_line:
            ...         break

        Technical Notes:
            - Uses WebSocketStreamManager for connection management
            - Automatic input validation and sanitization
            - Resource cleanup handled by WeakSet tracking
            - Stream limits prevent memory exhaustion
            - Thread pool manages WebSocket operations

        See Also:
            stream_tail_job_logs: HTTP-based alternative
            tail_job_logs: Protocol-agnostic wrapper method
        """
        if hasattr(self, 'long_poll_handler') and self.long_poll_handler:
            raise ClientError(400, '"websocket_tail_job_logs" does not support long polling')

        # Validate inputs using network utilities
        validated_pk = validate_resource_id(pk, 'job')
        validated_timeout = validate_timeout(stream_timeout)

        # Build WebSocket URL
        path = f'ray/jobs/{validated_pk}/logs/ws/'
        url = self._get_url(path, trailing_slash=True)
        ws_url = http_to_websocket_url(url)

        # Get headers and use WebSocket manager
        headers = self._get_headers()
        headers['Agent-Token'] = f'Token {self.agent_token}'
        context = f'job {validated_pk}'

        return self._websocket_manager.stream_logs(ws_url, headers, validated_timeout, context)

    def stream_tail_job_logs(self, pk, stream_timeout=10):
        """Stream job logs in real-time using HTTP chunked transfer encoding.

        Establishes an HTTP connection with chunked transfer encoding to stream
        job logs as they are generated. This method serves as a reliable fallback
        when WebSocket connections are not available or suitable.

        Args:
            pk (str): Job primary key or identifier. Must be alphanumeric with
                     optional hyphens/underscores, max 100 characters.
            stream_timeout (float, optional): Maximum time in seconds to wait for
                                            log data. Defaults to 10. Must be positive
                                            and cannot exceed 300 seconds.

        Returns:
            Generator[str, None, None]: A generator yielding log lines as strings.
                                      Each line includes a newline character.

        Raises:
            ClientError:
                - 400: If long polling is enabled (incompatible)
                - 400: If pk is empty, contains invalid characters, or too long
                - 400: If stream_timeout is not positive or exceeds maximum
                - 503: If connection to Ray cluster fails
                - 408: If connection or read timeout occurs
                - 404: If job is not found
                - 429: If stream limits are exceeded (lines, size, messages)
                - 500: If unexpected streaming error occurs

        Usage:
            >>> # Basic HTTP log streaming
            >>> for log_line in client.stream_tail_job_logs('job-12345'):
            ...     print(log_line.strip())

            >>> # With error handling and custom timeout
            >>> try:
            ...     for log_line in client.stream_tail_job_logs('job-12345', stream_timeout=60):
            ...         if 'COMPLETED' in log_line:
            ...             break
            ... except ClientError as e:
            ...     print(f"Streaming failed: {e}")

        Technical Notes:
            - Uses HTTPStreamManager for connection management
            - Automatic input validation and sanitization
            - Proper HTTP response cleanup on completion/error
            - Stream limits prevent memory exhaustion
            - Filters out oversized lines (>10KB) automatically
            - Connection reuse through requests session

        See Also:
            websocket_tail_job_logs: WebSocket-based alternative (preferred)
            tail_job_logs: Protocol-agnostic wrapper method
        """
        if hasattr(self, 'long_poll_handler') and self.long_poll_handler:
            raise ClientError(400, '"stream_tail_job_logs" does not support long polling')

        # Validate inputs using network utilities
        validated_pk = validate_resource_id(pk, 'job')
        validated_timeout = validate_timeout(stream_timeout)

        # Build HTTP URL and prepare request
        path = f'ray/jobs/{validated_pk}/logs/stream/'
        url = self._get_url(path, trailing_slash=True)
        headers = self._get_headers()
        headers['Agent-Token'] = f'Token {self.agent_token}'
        timeout = (self.timeout['connect'], validated_timeout)
        context = f'job {validated_pk}'

        return self._http_manager.stream_logs(url, headers, timeout, context)

    def tail_job_logs(self, pk, stream_timeout=10, protocol='stream'):
        """Tail job logs using either WebSocket or HTTP streaming.

        Args:
            pk: Job primary key
            stream_timeout: Timeout for streaming operations
            protocol: 'websocket' or 'stream' (default: 'stream')
        """
        # Validate protocol first
        if protocol not in ('websocket', 'stream'):
            raise ClientError(400, f'Unsupported protocol: {protocol}. Use "websocket" or "stream"')

        # Pre-validate common inputs using network utilities
        validate_resource_id(pk, 'job')
        validate_timeout(stream_timeout)

        try:
            if protocol == 'websocket':
                return self.websocket_tail_job_logs(pk, stream_timeout)
            else:  # protocol == 'stream'
                return self.stream_tail_job_logs(pk, stream_timeout)
        except ClientError:
            raise
        except Exception as e:
            # Fallback error handling using network utility
            sanitized_error = sanitize_error_message(str(e), f'job {pk}')
            raise ClientError(500, f'Protocol {protocol} failed: {sanitized_error}')

    def __del__(self):
        """Cleanup resources when object is destroyed."""
        try:
            if hasattr(self, '_thread_pool'):
                self._thread_pool.shutdown(wait=False)
        except Exception:
            pass  # Ignore cleanup errors during destruction

    def get_node(self, pk):
        path = f'nodes/{pk}/'
        return self._get(path)

    def list_nodes(self):
        path = 'nodes/'
        return self._get(path)

    def get_task(self, pk):
        path = f'tasks/{pk}/'
        return self._get(path)

    def list_tasks(self):
        path = 'tasks/'
        return self._get(path)

    def get_serve_application(self, pk):
        path = f'serve_applications/{pk}/'
        return self._get(path)

    def list_serve_applications(self):
        path = 'serve_applications/'
        return self._get(path)

    def delete_serve_application(self, pk):
        path = f'serve_applications/{pk}/'
        return self._delete(path)
