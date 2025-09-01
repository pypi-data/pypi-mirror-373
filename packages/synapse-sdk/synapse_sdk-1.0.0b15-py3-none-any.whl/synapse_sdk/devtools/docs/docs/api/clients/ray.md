---
id: ray
title: RayClient
sidebar_position: 4
---

# RayClient

Client for Apache Ray cluster management and monitoring functionality.

## Overview

The `RayClientMixin` provides comprehensive Ray cluster operations, including job management, real-time log streaming, node monitoring, and Ray Serve application control. It's designed as a mixin class that extends `BaseClient` with Ray-specific functionality.

## Key Features

- **Job Lifecycle Management**: Create, monitor, and manage Ray jobs
- **Real-time Log Streaming**: WebSocket and HTTP-based log tailing
- **Node & Task Monitoring**: Monitor cluster resources and task execution
- **Ray Serve Integration**: Deploy and manage Ray Serve applications
- **Robust Error Handling**: Input validation and sanitized error messages
- **Resource Management**: Automatic cleanup and connection tracking

## Constructor

```python
# RayClientMixin is typically used as a mixin
class RayClient(RayClientMixin):
    def __init__(self, base_url: str, timeout: dict = None):
        super().__init__(base_url, timeout)
```

### Parameters

- `base_url` (str): Ray cluster dashboard URL (e.g., "http://ray-head:8265")
- `timeout` (dict, optional): Connection and read timeout configuration

## Usage

```python
from synapse_sdk.clients.agent.ray import RayClientMixin
from synapse_sdk.clients.base import BaseClient

class RayClient(RayClientMixin, BaseClient):
    pass

client = RayClient(base_url="http://ray-head:8265")

# List all jobs
jobs = client.list_jobs()

# Get specific job details
job = client.get_job('job-12345')

# Stream logs in real-time
for log_line in client.tail_job_logs('job-12345'):
    print(log_line.strip())
```

## Job Operations

### `get_job(pk)`

Retrieve details for a specific job.

```python
job = client.get_job('job-12345')
print(f"Job status: {job['status']}")
```

### `list_jobs()`

List all jobs in the Ray cluster.

```python
jobs = client.list_jobs()
for job in jobs['results']:
    print(f"Job {job['id']}: {job['status']}")
```

### `list_job_logs(pk)`

Get static log entries for a job.

```python
logs = client.list_job_logs('job-12345')
```

## Real-time Log Streaming

### `tail_job_logs(pk, stream_timeout=10, protocol='stream')`

Stream job logs using either WebSocket or HTTP protocol.

```python
# HTTP streaming (default, more compatible)
for log_line in client.tail_job_logs('job-12345', protocol='stream'):
    print(log_line.strip())

# WebSocket streaming (lower latency)
for log_line in client.tail_job_logs('job-12345', protocol='websocket'):
    print(log_line.strip())

# With custom timeout
for log_line in client.tail_job_logs('job-12345', stream_timeout=30):
    if 'ERROR' in log_line:
        break
```

### `websocket_tail_job_logs(pk, stream_timeout=10)`

Stream logs via WebSocket for lowest latency.

```python
try:
    for log_line in client.websocket_tail_job_logs('job-12345'):
        print(log_line.strip())
        if 'COMPLETED' in log_line:
            break
except ClientError as e:
    print(f"WebSocket streaming failed: {e}")
```

### `stream_tail_job_logs(pk, stream_timeout=10)`

Stream logs via HTTP chunked transfer encoding.

```python
for log_line in client.stream_tail_job_logs('job-12345', stream_timeout=60):
    if 'FAILED' in log_line:
        print(f"Job failed: {log_line}")
        break
```

## Node Operations

### `get_node(pk)`

Get details for a specific cluster node.

```python
node = client.get_node('node-abc123')
print(f"Node status: {node['alive']}")
```

### `list_nodes()`

List all nodes in the Ray cluster.

```python
nodes = client.list_nodes()
for node in nodes['results']:
    print(f"Node {node['node_id']}: {node['state']}")
```

## Task Operations

### `get_task(pk)`

Retrieve details for a specific task.

```python
task = client.get_task('task-xyz789')
```

### `list_tasks()`

List all tasks in the cluster.

```python
tasks = client.list_tasks()
```

## Ray Serve Operations

### `get_serve_application(pk)`

Get details for a Ray Serve application.

```python
app = client.get_serve_application('app-123')
print(f"Application status: {app['status']}")
```

### `list_serve_applications()`

List all Ray Serve applications.

```python
apps = client.list_serve_applications()
```

### `delete_serve_application(pk)`

Delete a Ray Serve application.

```python
client.delete_serve_application('app-123')
```

## Error Handling

All methods include robust error handling with specific `ClientError` exceptions:

```python
from synapse_sdk.clients.exceptions import ClientError

try:
    for log_line in client.tail_job_logs('invalid-job'):
        print(log_line)
except ClientError as e:
    if e.status == 400:
        print("Invalid job ID or parameters")
    elif e.status == 404:
        print("Job not found")
    elif e.status == 503:
        print("Connection to Ray cluster failed")
    else:
        print(f"Unexpected error: {e}")
```

### Common Error Codes

- **400**: Invalid parameters (job ID, timeout, protocol)
- **404**: Resource not found (job, node, task, application)
- **408**: Connection or read timeout
- **429**: Stream limits exceeded
- **500**: WebSocket library unavailable or internal error
- **503**: Ray cluster connection failed

## Resource Management

The RayClient includes automatic resource management:

- **Thread Pool**: 5 worker threads for concurrent operations
- **Connection Tracking**: WeakSet for active connections
- **Stream Limits**: Prevents memory exhaustion
- **Automatic Cleanup**: Resources cleaned up on destruction

### Stream Limits

Default limits for log streaming:

- Max messages: 10,000
- Max lines: 50,000
- Max bytes: 50MB
- Max message size: 10KB
- Queue size: 1,000

## Best Practices

### 1. Protocol Selection

```python
# Use WebSocket for lowest latency when available
try:
    logs = client.tail_job_logs(job_id, protocol='websocket')
except ClientError:
    # Fallback to HTTP streaming
    logs = client.tail_job_logs(job_id, protocol='stream')
```

### 2. Timeout Management

```python
# Use appropriate timeouts for long-running jobs
for log_line in client.tail_job_logs(job_id, stream_timeout=300):
    process_log_line(log_line)
```

### 3. Error Recovery

```python
import time

def robust_log_streaming(client, job_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            for log_line in client.tail_job_logs(job_id):
                yield log_line
            break
        except ClientError as e:
            if e.status == 503 and attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
                continue
            raise
```

### 4. Resource Cleanup

```python
# Context manager for proper cleanup
class RayClientContext:
    def __init__(self, base_url):
        self.client = RayClient(base_url)

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Cleanup handled automatically by RayClient.__del__()
        pass

with RayClientContext("http://ray-head:8265") as client:
    for log_line in client.tail_job_logs('job-12345'):
        print(log_line.strip())
```

## Thread Safety

RayClient is designed for concurrent use with proper thread safety mechanisms:

- Thread pool for background operations
- WeakSet for connection tracking
- Proper resource cleanup mechanisms

## See Also

- [AgentClient](./agent.md) - For agent-specific operations
- [BaseClient](./base.md) - Base client implementation
- [Network Utilities](../utils/network.md) - Streaming and validation utilities
