---
id: cli-usage
title: CLI Usage Guide
sidebar_position: 4
---

# CLI Usage Guide

The Synapse SDK provides a powerful interactive CLI for managing your development workflow, from configuration to plugin development and code editing.

## Getting Started

Launch the interactive CLI:

```bash
synapse
```

Or run specific commands directly:

```bash
# Start development tools immediately
synapse --dev-tools

# Show help
synapse --help
```

## Main Menu Options

When you run `synapse`, you'll see the main menu:

```
🚀 Synapse SDK
Select an option:
  🌐 Run Dev Tools
  💻 Open Code-Server IDE
  ⚙️  Configuration
  🔌 Plugin Management
  🚪 Exit
```

## 🌐 Run Dev Tools

Launches the Synapse development tools dashboard with:

- **Interactive UI**: Web-based dashboard for managing agents and jobs
- **Real-time Monitoring**: Live view of agent status and job execution
- **Plugin Management**: Upload, test, and manage plugins through the UI

### Usage
```bash
# Launch dev tools from CLI menu
synapse

# Or start directly
synapse --dev-tools
```

## 💻 Open Code-Server IDE

Opens a web-based VS Code environment for plugin development. Supports both agent-based and local code-server instances.

### Agent Code-Server

Connect to a remote code-server running on an agent:

- **Automatic Setup**: Synapse configures the workspace and installs dependencies
- **Plugin Encryption**: Local plugin code is encrypted and securely transferred
- **Workspace Sync**: Your local project is available in the agent environment

### Local Code-Server

Launch a local code-server instance:

- **Port Detection**: Automatically reads port from `~/.config/code-server/config.yaml`
- **Folder Parameter**: Opens with correct workspace directory
- **Browser Integration**: Automatically opens browser with proper URL

### Usage Examples

```bash
# Interactive menu (recommended)
synapse
# Select "💻 Open Code-Server IDE"

# Direct command
synapse code-server

# With specific options
synapse code-server --agent my-agent --workspace /path/to/project

# Don't open browser automatically
synapse code-server --no-open-browser
```

### Code-Server Options

| Option | Description | Default |
|--------|-------------|---------|
| `--agent` | Specific agent ID to use | Current agent or prompt |
| `--workspace` | Project directory path | Current directory |
| `--open-browser/--no-open-browser` | Open browser automatically | `--open-browser` |

### Local Code-Server Installation

If code-server isn't installed locally, the CLI provides installation instructions:

```bash
# Recommended: Install script
curl -fsSL https://code-server.dev/install.sh | sh

# Using npm
npm install -g code-server

# Using yarn
yarn global add code-server
```

For more options, visit: https://coder.com/docs/code-server/latest/install

## ⚙️ Configuration

Interactive configuration wizard for setting up:

- **Backend Connection**: Configure API endpoints and authentication
- **Agent Selection**: Choose and configure development agents
- **Token Management**: Manage access tokens and authentication

### Configuration Files

Synapse stores configuration in:
- **Backend Config**: `~/.synapse/devtools.yaml`
- **Agent Config**: `~/.synapse/devtools.yaml` (agent section)
- **Code-Server Config**: `~/.config/code-server/config.yaml`

## 🔌 Plugin Management

Comprehensive plugin development and management tools:

### Create New Plugin

```bash
synapse
# Select "🔌 Plugin Management" → "Create new plugin"
```

Interactive wizard creates:
- Plugin directory structure
- Configuration files (`config.yaml`)
- Example plugin code
- Requirements and dependencies

### Run Plugin Locally

Test plugins in different environments:

```bash
# Script execution (local)
synapse plugin run my_action '{"param": "value"}' --run-by script

# Agent execution (remote)
synapse plugin run my_action '{"param": "value"}' --run-by agent

# Backend execution (cloud)
synapse plugin run my_action '{"param": "value"}' --run-by backend
```

### Publish Plugin

Deploy plugins to your Synapse backend:

```bash
synapse
# Select "🔌 Plugin Management" → "Publish plugin"
```

Options:
- **Debug Mode**: Test deployment with verbose logging
- **Production Mode**: Deploy for live use

## Command Reference

### Main Commands

```bash
# Interactive CLI (main menu)
synapse

# Development tools
synapse --dev-tools

# Direct commands
synapse config         # Configuration wizard
synapse devtools       # Development dashboard
synapse code-server    # Code editing environment
synapse plugin         # Plugin management
```

### Code-Server Command

```bash
synapse code-server [OPTIONS]

Options:
  --agent TEXT                    Agent name or ID
  --open-browser / --no-open-browser
                                  Open in browser [default: open-browser]
  --workspace TEXT                Workspace directory path (defaults to current directory)
  --help                          Show this message and exit.
```

### Plugin Commands

```bash
# Create plugin
synapse plugin create

# Run plugin
synapse plugin run ACTION PARAMS [OPTIONS]

# Publish plugin  
synapse plugin publish [OPTIONS]
```

## Tips & Best Practices

### Code-Server Development

1. **Plugin Detection**: When opening code-server, Synapse automatically detects if your workspace contains a plugin and encrypts it for secure transfer to agents.

2. **Workspace Paths**: Agent workspaces typically use `/home/coder/workspace` - this is normal for containerized environments.

3. **Port Configuration**: Local code-server port is read from your config file, defaulting to 8070 if not configured.

### Configuration Management

1. **Token Security**: Store API tokens securely and rotate them regularly
2. **Agent Selection**: Use descriptive agent names to identify their purpose
3. **Backend URLs**: Ensure backend URLs are accessible from your development environment

### Plugin Development

1. **Local Testing**: Always test plugins locally with `--run-by script` before deploying
2. **Debug Mode**: Use debug mode for initial deployments to catch issues early
3. **Version Control**: Use git to track plugin changes and manage versions

## Troubleshooting

### Code-Server Issues

**Problem**: "Code-server is not available"
- **Solution**: Ensure the agent has code-server support enabled

**Problem**: Browser doesn't open automatically
- **Solution**: Manually copy the provided URL to your browser

**Problem**: Wrong port displayed
- **Solution**: Check `~/.config/code-server/config.yaml` for correct port configuration

### Configuration Issues

**Problem**: "No backend configured"
- **Solution**: Run `synapse config` to set up backend connection

**Problem**: "Invalid token (401)"
- **Solution**: Generate a new API token and update configuration

**Problem**: "Connection timeout"
- **Solution**: Check network connectivity and backend URL accessibility

### Plugin Issues

**Problem**: Plugin not detected in workspace
- **Solution**: Ensure your directory has a valid `config.yaml` file

**Problem**: Plugin execution fails
- **Solution**: Check plugin dependencies and syntax, test locally first

For more troubleshooting help, see the [Troubleshooting Guide](./troubleshooting.md).