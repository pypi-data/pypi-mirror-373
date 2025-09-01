---
id: backend
title: BackendClient
sidebar_position: 1
---

# BackendClient

Main client for interacting with the Synapse backend API.

## Overview

The `BackendClient` provides comprehensive access to all backend operations including data management, plugin execution, annotations, and machine learning workflows. It aggregates functionality from multiple specialized mixins.

## Constructor

```python
BackendClient(
    base_url: str,
    api_token: str = None,
    agent_token: str = None,
    timeout: dict = None
)
```

### Parameters

- **base_url** (`str`): The base URL of the Synapse backend API
- **api_token** (`str`, optional): API authentication token. Can also be set via `SYNAPSE_API_TOKEN` environment variable
- **agent_token** (`str`, optional): Agent authentication token. Can also be set via `SYNAPSE_AGENT_TOKEN` environment variable
- **timeout** (`dict`, optional): Custom timeout settings. Defaults to `{'connect': 5, 'read': 30}`

### Example

```python
from synapse_sdk.clients.backend import BackendClient

# Create client with explicit token
client = BackendClient(
    base_url="https://api.synapse.sh",
    api_token="your-api-token"
)

# Or use environment variables
import os
os.environ['SYNAPSE_API_TOKEN'] = "your-api-token"
client = BackendClient(base_url="https://api.synapse.sh")
```

## See Also

- [AgentClient](./agent.md) - For agent-specific operations
- [BaseClient](./base.md) - Base client implementation
