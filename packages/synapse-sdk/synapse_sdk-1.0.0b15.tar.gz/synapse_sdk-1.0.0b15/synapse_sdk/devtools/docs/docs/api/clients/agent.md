---
id: agent
title: AgentClient
sidebar_position: 2
---

# AgentClient

Client for agent-specific operations and distributed execution.

## Overview

The `AgentClient` provides access to agent operations, including plugin execution, job management, and distributed computing integration.

## Constructor

```python
AgentClient(
    base_url: str,
    agent_token: str = None,
    timeout: dict = None
)
```

## Usage

```python
from synapse_sdk.clients.agent import AgentClient

client = AgentClient(
    base_url="https://api.synapse.sh",
    agent_token="your-agent-token"
)
```

## Methods

Coming soon - detailed API documentation for AgentClient methods.

## See Also

- [BackendClient](./backend.md) - For backend operations
- [BaseClient](./base.md) - Base client implementation