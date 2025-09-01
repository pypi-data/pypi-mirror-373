---
id: network
title: Network Utilities
sidebar_position: 4
---

# Network Utilities

Comprehensive networking utilities for streaming, validation, and connection management.

## Overview

The `synapse_sdk.utils.network` module provides essential networking components used by Ray and other clients for secure, robust streaming operations and input validation.

## StreamLimits

Configuration class for streaming operation limits to prevent resource exhaustion.

### Constructor

```python
from synapse_sdk.utils.network import StreamLimits

limits = StreamLimits(
    max_messages=10000,
    max_lines=50000,
    max_bytes=50 * 1024 * 1024,  # 50MB
    max_message_size=10240,      # 10KB
    queue_size=1000,
    exception_queue_size=10
)
```

### Parameters

- `max_messages` (int): Maximum number of messages to process (default: 10,000)
- `max_lines` (int): Maximum number of lines to stream (default: 50,000)
- `max_bytes` (int): Maximum total bytes to process (default: 50MB)
- `max_message_size` (int): Maximum size per message (default: 10KB)
- `queue_size` (int): Internal queue size for message buffering (default: 1,000)
- `exception_queue_size` (int): Queue size for exception handling (default: 10)

### Usage

```python
# Custom limits for high-volume streaming
custom_limits = StreamLimits(
    max_messages=50000,
    max_lines=100000,
    max_bytes=100 * 1024 * 1024  # 100MB
)

# Use with stream managers
websocket_manager = WebSocketStreamManager(thread_pool, custom_limits)
```

## WebSocketStreamManager

Manages WebSocket connections for real-time log streaming with automatic error handling and resource cleanup.

### Constructor

```python
from synapse_sdk.utils.network import WebSocketStreamManager
from concurrent.futures import ThreadPoolExecutor

thread_pool = ThreadPoolExecutor(max_workers=5)
limits = StreamLimits()
manager = WebSocketStreamManager(thread_pool, limits)
```

### Methods

#### `stream_logs(ws_url, headers, timeout, context)`

Stream logs from a WebSocket endpoint.

```python
# Stream logs with error handling
try:
    for log_line in manager.stream_logs(
        ws_url="wss://ray-cluster:8265/logs/ws/",
        headers={"Authorization": "Bearer token"},
        timeout=30.0,
        context="job job-12345"
    ):
        print(log_line.strip())
except ClientError as e:
    print(f"Streaming failed: {e}")
```

### Error Handling

- **500**: WebSocket library not available
- **503**: Connection failed
- **408**: Connection timeout
- **429**: Stream limits exceeded

## HTTPStreamManager

Manages HTTP streaming connections using chunked transfer encoding for reliable log streaming.

### Constructor

```python
from synapse_sdk.utils.network import HTTPStreamManager
import requests

session = requests.Session()
limits = StreamLimits()
manager = HTTPStreamManager(session, limits)
```

### Methods

#### `stream_logs(url, headers, timeout, context)`

Stream logs from an HTTP endpoint with chunked transfer encoding.

```python
# Stream logs with custom timeout
for log_line in manager.stream_logs(
    url="http://ray-cluster:8265/logs/stream",
    headers={"Authorization": "Bearer token"},
    timeout=(5, 60),  # (connect, read) timeout
    context="job job-12345"
):
    if 'ERROR' in log_line:
        print(f"Error detected: {log_line}")
```

### Features

- **Automatic Resource Cleanup**: HTTP responses properly closed
- **Line Size Filtering**: Oversized lines (>10KB) automatically filtered
- **Stream Limits**: Prevents memory exhaustion
- **Error Recovery**: Robust error handling with proper cleanup

### Error Handling

- **503**: Connection refused or network error
- **408**: Connection or read timeout
- **404**: Endpoint not found
- **429**: Stream limits exceeded
- **500**: Unexpected streaming error

## Validation Functions

### `validate_resource_id(resource_id, resource_name='resource')`

Validates resource identifiers to prevent injection attacks.

```python
from synapse_sdk.utils.network import validate_resource_id

# Valid usage
job_id = validate_resource_id('job-12345', 'job')
node_id = validate_resource_id('node_abc_123', 'node')

# Invalid usage raises ClientError
try:
    validate_resource_id('job/../malicious', 'job')
except ClientError as e:
    print(f"Invalid ID: {e}")  # Status 400
```

#### Validation Rules

- Must not be empty
- Only alphanumeric characters, hyphens, and underscores allowed
- Maximum length: 100 characters
- Pattern: `^[a-zA-Z0-9\-_]+$`

#### Parameters

- `resource_id` (Any): The ID to validate (converted to string)
- `resource_name` (str): Name for error messages (default: 'resource')

#### Returns

- `str`: Validated resource ID

#### Raises

- `ClientError` (400): If validation fails

### `validate_timeout(timeout, max_timeout=300)`

Validates timeout values with bounds checking.

```python
from synapse_sdk.utils.network import validate_timeout

# Valid timeouts
timeout = validate_timeout(30)      # 30 seconds
timeout = validate_timeout(10.5)    # 10.5 seconds

# Invalid timeouts raise ClientError
try:
    validate_timeout(-1)     # Negative timeout
    validate_timeout(500)    # Exceeds maximum
except ClientError as e:
    print(f"Invalid timeout: {e}")  # Status 400
```

#### Parameters

- `timeout` (int|float): Timeout value in seconds
- `max_timeout` (int): Maximum allowed timeout (default: 300)

#### Returns

- `float`: Validated timeout value

#### Raises

- `ClientError` (400): If timeout is invalid

## URL Utilities

### `http_to_websocket_url(http_url)`

Converts HTTP URLs to WebSocket URLs.

```python
from synapse_sdk.utils.network import http_to_websocket_url

# Convert URLs
ws_url = http_to_websocket_url("http://ray-cluster:8265/logs/")
# Result: "ws://ray-cluster:8265/logs/"

wss_url = http_to_websocket_url("https://ray-cluster:8265/logs/")
# Result: "wss://ray-cluster:8265/logs/"
```

#### Parameters

- `http_url` (str): HTTP or HTTPS URL

#### Returns

- `str`: WebSocket URL (ws:// or wss://)

## Error Utilities

### `sanitize_error_message(message, context)`

Sanitizes error messages to prevent information leakage while maintaining debugging context.

```python
from synapse_sdk.utils.network import sanitize_error_message

# Sanitize errors for logging
clean_message = sanitize_error_message(
    "Connection failed: Invalid token abc123",
    "job job-12345"
)
# Result: Sanitized error message with context
```

#### Parameters

- `message` (str): Original error message
- `context` (str): Context for debugging (e.g., "job job-12345")

#### Returns

- `str`: Sanitized error message

## Complete Example

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from synapse_sdk.utils.network import (
    StreamLimits,
    WebSocketStreamManager,
    HTTPStreamManager,
    validate_resource_id,
    validate_timeout,
    http_to_websocket_url
)

class StreamingExample:
    def __init__(self):
        # Setup components
        self.thread_pool = ThreadPoolExecutor(max_workers=3)
        self.limits = StreamLimits(max_lines=10000)
        self.ws_manager = WebSocketStreamManager(self.thread_pool, self.limits)

        # HTTP session for HTTP streaming
        import requests
        self.session = requests.Session()
        self.http_manager = HTTPStreamManager(self.session, self.limits)

    def stream_job_logs(self, job_id, protocol='websocket'):
        # Validate inputs
        validated_id = validate_resource_id(job_id, 'job')
        timeout = validate_timeout(30)

        if protocol == 'websocket':
            return self._websocket_stream(validated_id, timeout)
        else:
            return self._http_stream(validated_id, timeout)

    def _websocket_stream(self, job_id, timeout):
        url = f"http://ray-cluster:8265/jobs/{job_id}/logs/"
        ws_url = http_to_websocket_url(url)
        headers = {"Authorization": "Bearer token"}
        context = f"job {job_id}"

        return self.ws_manager.stream_logs(ws_url, headers, timeout, context)

    def _http_stream(self, job_id, timeout):
        url = f"http://ray-cluster:8265/jobs/{job_id}/logs/stream"
        headers = {"Authorization": "Bearer token"}
        timeout_tuple = (5, timeout)
        context = f"job {job_id}"

        return self.http_manager.stream_logs(url, headers, timeout_tuple, context)

# Usage
example = StreamingExample()

# Stream with WebSocket
for log_line in example.stream_job_logs('job-12345', 'websocket'):
    print(log_line.strip())

# Stream with HTTP fallback
for log_line in example.stream_job_logs('job-12345', 'http'):
    print(log_line.strip())
```

## Best Practices

### 1. Resource Management

```python
# Always use proper cleanup
thread_pool = ThreadPoolExecutor(max_workers=5)
try:
    manager = WebSocketStreamManager(thread_pool, StreamLimits())
    # Use manager...
finally:
    thread_pool.shutdown(wait=True)
```

### 2. Error Handling

```python
from synapse_sdk.clients.exceptions import ClientError

try:
    job_id = validate_resource_id(user_input, 'job')
    timeout = validate_timeout(user_timeout)
    # Proceed with validated inputs...
except ClientError as e:
    logger.error(f"Validation failed: {e}")
    return error_response(e.status, str(e))
```

### 3. Stream Limits Configuration

```python
# Configure limits based on use case
production_limits = StreamLimits(
    max_messages=20000,      # Higher for production
    max_lines=100000,        # More lines allowed
    max_bytes=200 * 1024 * 1024,  # 200MB for large logs
    queue_size=2000          # Larger buffer
)
```

## See Also

- [RayClient](../clients/ray.md) - Primary consumer of network utilities
- [File Utils](./file.md) - File operations and handling
- [Storage](./storage.md) - Storage providers
