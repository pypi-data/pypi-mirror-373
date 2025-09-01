---
id: index
title: API Reference
sidebar_position: 1
---

# API Reference

Complete reference documentation for Synapse SDK classes and functions.

## Overview

The Synapse SDK API is organized into the following main modules:

### [Clients](./clients/backend.md)
Client classes for interacting with backend services and agents.

- **[BackendClient](./clients/backend.md)** - Main client for backend operations
- **[AgentClient](./clients/agent.md)** - Client for agent-specific operations  
- **[RayClient](./clients/ray.md)** - Client for Ray cluster management and monitoring
- **[BaseClient](./clients/base.md)** - Base class for all clients

Core plugin system components.

### [Utilities](./utils/file.md)
Helper functions and utilities.

- **[File Utils](./utils/file.md)** - File operations and handling
- **[Network](./utils/network.md)** - Streaming, validation, and connection management
- **[Storage](./utils/storage.md)** - Storage providers (S3, GCS, SFTP)
- **[Types](./utils/types.md)** - Custom types and fields

## Quick Reference

### Creating a Client

```python
from synapse_sdk.clients.backend import BackendClient

client = BackendClient(
    base_url="https://api.synapse.sh",
    api_token="your-api-token"
)
```

### Running a Plugin

### Creating a Plugin Action

## Type Annotations

## File Handling
