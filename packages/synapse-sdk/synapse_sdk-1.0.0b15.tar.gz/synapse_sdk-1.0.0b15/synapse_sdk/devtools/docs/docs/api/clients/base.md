---
id: base
title: BaseClient
sidebar_position: 3
---

# BaseClient

Base class for all Synapse SDK clients.

## Overview

The `BaseClient` provides common functionality for HTTP operations, error handling, and request management used by all other clients.

## Features

- HTTP request handling with retry logic
- Automatic timeout management
- File upload/download capabilities
- Pydantic model validation
- Connection pooling

## Usage

```python
from synapse_sdk.clients.base import BaseClient

# BaseClient is typically not used directly
# Use BackendClient or AgentClient instead
```

## See Also

- [BackendClient](./backend.md) - Main client implementation
- [AgentClient](./agent.md) - Agent-specific operations