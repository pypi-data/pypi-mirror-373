import asyncio
import queue as queue_module
import re
import ssl
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Any, Dict, Generator, Optional
from urllib.parse import urlparse, urlunparse

import requests

from synapse_sdk.clients.exceptions import ClientError


@dataclass
class StreamLimits:
    """Configuration for streaming limits."""

    max_messages: int = 10000
    max_lines: int = 50000
    max_bytes: int = 50 * 1024 * 1024  # 50MB
    max_message_size: int = 10240  # 10KB
    queue_size: int = 1000
    exception_queue_size: int = 10


def validate_resource_id(resource_id: Any, resource_name: str = 'resource') -> str:
    """Validate resource ID to prevent injection attacks."""
    if not resource_id:
        raise ClientError(400, f'{resource_name} ID cannot be empty')

    # Allow numeric IDs and UUID formats
    id_str = str(resource_id)
    if not re.match(r'^[a-zA-Z0-9\-_]+$', id_str):
        raise ClientError(400, f'Invalid {resource_name} ID format')

    if len(id_str) > 100:
        raise ClientError(400, f'{resource_name} ID too long')

    return id_str


def validate_timeout(timeout: Any, max_timeout: int = 300) -> float:
    """Validate timeout value with bounds checking."""
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        raise ClientError(400, 'Timeout must be a positive number')

    if timeout > max_timeout:
        raise ClientError(400, f'Timeout cannot exceed {max_timeout} seconds')

    return float(timeout)


def sanitize_error_message(error_msg: str, context: str = '') -> str:
    """Sanitize error messages to prevent information disclosure."""
    sanitized = str(error_msg)[:100]
    # Remove any potential sensitive information
    sanitized = re.sub(r'["\']([^"\']*)["\']', '"[REDACTED]"', sanitized)

    if context:
        return f'{context}: {sanitized}'
    return sanitized


def http_to_websocket_url(url: str) -> str:
    """Convert HTTP/HTTPS URL to WebSocket URL safely."""
    try:
        parsed = urlparse(url)
        if parsed.scheme == 'http':
            ws_scheme = 'ws'
        elif parsed.scheme == 'https':
            ws_scheme = 'wss'
        else:
            raise ClientError(400, f'Invalid URL scheme: {parsed.scheme}')

        ws_url = urlunparse((ws_scheme, parsed.netloc, parsed.path, parsed.params, parsed.query, parsed.fragment))
        return ws_url
    except Exception as e:
        raise ClientError(400, f'Invalid URL format: {str(e)[:50]}')


def check_library_available(library_name: str) -> bool:
    """Check if optional library is available."""
    try:
        __import__(library_name)
        return True
    except ImportError:
        return False


class WebSocketStreamManager:
    """Manages secure WebSocket streaming with rate limiting and error handling."""

    def __init__(self, thread_pool: ThreadPoolExecutor, limits: Optional[StreamLimits] = None):
        self.thread_pool = thread_pool
        self.limits = limits or StreamLimits()

    def stream_logs(
        self, ws_url: str, headers: Dict[str, str], timeout: float, context: str
    ) -> Generator[str, None, None]:
        """Stream logs from WebSocket with proper error handling and cleanup."""
        if not check_library_available('websockets'):
            raise ClientError(500, 'websockets library not available for WebSocket connections')

        try:
            import websockets

            # Use bounded queues to prevent memory exhaustion
            message_queue = queue_module.Queue(maxsize=self.limits.queue_size)
            exception_queue = queue_module.Queue(maxsize=self.limits.exception_queue_size)

            async def websocket_client():
                try:
                    # Add SSL verification and proper timeouts
                    connect_kwargs = {
                        'extra_headers': headers,
                        'close_timeout': timeout,
                        'ping_timeout': timeout,
                        'ping_interval': timeout // 2,
                    }

                    # For secure connections, add SSL context
                    if ws_url.startswith('wss://'):
                        ssl_context = ssl.create_default_context()
                        ssl_context.check_hostname = True
                        ssl_context.verify_mode = ssl.CERT_REQUIRED
                        connect_kwargs['ssl'] = ssl_context

                    async with websockets.connect(ws_url, **connect_kwargs) as websocket:
                        message_count = 0

                        async for message in websocket:
                            message_count += 1
                            if message_count > self.limits.max_messages:
                                exception_queue.put_nowait(ClientError(429, f'Message limit exceeded for {context}'))
                                break

                            # Validate message size
                            if len(str(message)) > self.limits.max_message_size:
                                continue

                            try:
                                message_queue.put_nowait(f'{message}\n')
                            except queue_module.Full:
                                exception_queue.put_nowait(ClientError(429, f'Message queue full for {context}'))
                                break

                        message_queue.put_nowait(None)  # Signal end

                except websockets.exceptions.ConnectionClosed:
                    exception_queue.put_nowait(ClientError(503, f'WebSocket connection closed for {context}'))
                except asyncio.TimeoutError:
                    exception_queue.put_nowait(ClientError(408, f'WebSocket timed out for {context}'))
                except Exception as e:
                    sanitized_error = sanitize_error_message(str(e), context)
                    exception_queue.put_nowait(ClientError(500, sanitized_error))

            # Use thread pool instead of raw threading
            future = self.thread_pool.submit(lambda: asyncio.run(websocket_client()))

            # Yield messages with proper cleanup
            try:
                while True:
                    # Check for exceptions first
                    try:
                        exception = exception_queue.get_nowait()
                        raise exception
                    except queue_module.Empty:
                        pass

                    # Get message with timeout
                    try:
                        message = message_queue.get(timeout=1.0)
                        if message is None:  # End signal
                            break
                        yield message
                    except queue_module.Empty:
                        # Check if future is done
                        if future.done():
                            try:
                                future.result()  # This will raise any exception
                                break  # Normal completion
                            except Exception:
                                break  # Error already in queue
                        continue

            finally:
                # Cleanup: cancel future if still running
                if not future.done():
                    future.cancel()

        except ImportError:
            raise ClientError(500, 'websockets library not available for WebSocket connections')
        except Exception as e:
            if isinstance(e, ClientError):
                raise
            sanitized_error = sanitize_error_message(str(e), context)
            raise ClientError(500, sanitized_error)


class HTTPStreamManager:
    """Manages HTTP streaming with rate limiting and proper resource cleanup."""

    def __init__(self, requests_session: requests.Session, limits: Optional[StreamLimits] = None):
        self.requests_session = requests_session
        self.limits = limits or StreamLimits()

    def stream_logs(
        self, url: str, headers: Dict[str, str], timeout: tuple, context: str
    ) -> Generator[str, None, None]:
        """Stream logs from HTTP endpoint with proper error handling and cleanup."""
        response = None
        try:
            # Use timeout for streaming to prevent hanging
            response = self.requests_session.get(url, headers=headers, stream=True, timeout=timeout)
            response.raise_for_status()

            # Set up streaming with timeout and size limits
            line_count = 0
            total_bytes = 0

            try:
                for line in response.iter_lines(decode_unicode=True, chunk_size=1024):
                    if line:
                        line_count += 1
                        total_bytes += len(line.encode('utf-8'))

                        # Rate limiting checks
                        if line_count > self.limits.max_lines:
                            raise ClientError(429, f'Line limit exceeded for {context}')

                        if total_bytes > self.limits.max_bytes:
                            raise ClientError(429, f'Size limit exceeded for {context}')

                        # Validate line size
                        if len(line) > self.limits.max_message_size:
                            continue

                        yield f'{line}\n'

            except requests.exceptions.ChunkedEncodingError:
                raise ClientError(503, f'Log stream interrupted for {context}')
            except requests.exceptions.ReadTimeout:
                raise ClientError(408, f'Log stream timed out for {context}')

        except requests.exceptions.ConnectTimeout:
            raise ClientError(408, f'Failed to connect to log stream for {context}')
        except requests.exceptions.ReadTimeout:
            raise ClientError(408, f'Log stream read timeout for {context}')
        except requests.exceptions.ConnectionError as e:
            if 'Connection refused' in str(e):
                raise ClientError(503, f'Agent connection refused for {context}')
            else:
                sanitized_error = sanitize_error_message(str(e), context)
                raise ClientError(503, f'Agent connection error: {sanitized_error}')
        except requests.exceptions.HTTPError as e:
            if hasattr(e.response, 'status_code'):
                status_code = e.response.status_code
            else:
                status_code = 500
            raise ClientError(status_code, f'HTTP error streaming logs for {context}')
        except Exception as e:
            if isinstance(e, ClientError):
                raise
            sanitized_error = sanitize_error_message(str(e), context)
            raise ClientError(500, sanitized_error)
        finally:
            # Ensure response is properly closed
            if response is not None:
                try:
                    response.close()
                except Exception:
                    pass  # Ignore cleanup errors


def clean_url(url, remove_query_params=True, remove_fragment=True):
    parsed = urlparse(url)
    query = '' if remove_query_params else parsed.query
    fragment = '' if remove_fragment else parsed.fragment

    return urlunparse((
        parsed.scheme,
        parsed.netloc,
        parsed.path,
        parsed.params,
        query,
        fragment,
    ))


def get_available_ports_host(start_port=8900, end_port=8990):
    import nmap

    nm = nmap.PortScanner()

    scan_range = f'{start_port}-{end_port}'
    nm.scan(hosts='host.docker.internal', arguments=f'-p {scan_range}')

    try:
        open_ports = nm['host.docker.internal']['tcp'].keys()
        open_ports = [int(port) for port in open_ports]
    except KeyError:
        open_ports = []

    for port in range(start_port, end_port + 1):
        if port not in open_ports:
            return port

    raise IOError(f'No free ports available in range {start_port}-{end_port}')
