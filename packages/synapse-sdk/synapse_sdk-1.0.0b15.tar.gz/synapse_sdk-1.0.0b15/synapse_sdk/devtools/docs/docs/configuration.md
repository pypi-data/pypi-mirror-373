---
id: configuration
title: Configuration
sidebar_position: 8
---

# Configuration

Configure Synapse SDK for your environment and use cases.

## Configuration Methods

There are three ways to configure Synapse SDK:

1. **Synapse CLI**
2. **Environment variables**
3. **Configuration file**

## CLI

The interactive configuration menu provides an easy way to configure your Synapse SDK:

```bash
$ synapse config
```

This will open an interactive menu where you can:
- Configure backend host and API token
- Select or manually configure an agent
- View current configuration

### Key Features:
- **Plain text token display**: Tokens are shown in plain text for easy verification
- **Connection testing**: After configuring backend or agent, the connection is automatically tested
- **No startup delays**: Connection checks only happen when you configure settings, not on CLI startup

## Configuration File

Create a configuration file at `~/.synapse/config.json`:

```json
{
  "backend": {
    "host": "https://api.synapse.sh",
    "token": "your-api-token"
  },
  "agent": {
    "id": "agent-uuid-123",
    "name": "My Development Agent",
    "token": "your-agent-token"
  }
}
```

## Plugin Management

The CLI provides an interactive plugin management interface:

```bash
$ synapse
# Select "Plugin Management"
```

### Available Options:

1. **Create new plugin**: Creates a new plugin from templates using cookiecutter
2. **Run plugin locally**: Interactive interface to run plugins with configurable parameters
3. **Publish plugin**: Publishes plugins to the configured backend with debug mode option

### Plugin Publishing

When publishing plugins:
- **Debug mode**: Enabled by default for development
- **Backend integration**: Uses your configured backend settings
- **Connection testing**: Verifies backend connection before publishing
- **Error handling**: Stops on errors and waits for user acknowledgment

### Plugin Development Workflow

1. **Create**: Use the CLI to create a new plugin template
2. **Develop**: Write your plugin code following the generated structure
3. **Test**: Run plugins locally through the interactive interface
4. **Publish**: Deploy to your configured backend with debug options
