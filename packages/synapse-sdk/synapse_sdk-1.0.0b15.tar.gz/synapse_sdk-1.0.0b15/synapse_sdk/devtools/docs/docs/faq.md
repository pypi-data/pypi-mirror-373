---
id: faq
title: Frequently Asked Questions
sidebar_position: 9
---

# Frequently Asked Questions

Common questions and answers about Synapse SDK.

## Installation & Setup

### Q: What Python versions are supported?

Synapse SDK requires **Python 3.10 or higher**.

```bash
pip install "synapse-sdk[all,devtools]"
```

### Q: How do I install code-server for local development?

You have several options:

```bash
# Recommended: Install script
curl -fsSL https://code-server.dev/install.sh | sh

# Using npm
npm install -g code-server

# Using yarn
yarn global add code-server
```

For more installation methods, visit: [code-server installation guide](https://coder.com/docs/code-server/latest/install)

## CLI Usage

### Q: How do I start the Synapse CLI?

Simply run:

```bash
synapse
```

This opens the interactive menu where you can access all Synapse features.

### Q: What's the difference between agent and local code-server?

- **Agent Code-Server**: Runs on a remote agent with your project files synced. Includes plugin encryption and secure transfer.
- **Local Code-Server**: Runs on your local machine. Faster startup, uses your local environment and settings.

### Q: How do I configure the code-server port?

Code-server port is automatically detected from `~/.config/code-server/config.yaml`. If no config exists, it defaults to port 8070.

Example config:

```yaml
bind-addr: 127.0.0.1:8070
auth: password
password: your-password-here
cert: false
```

### Q: Why does the agent workspace path differ from my local path?

Agents run in containerized environments where your local project is mounted to `/home/coder/workspace`. This is normal and ensures consistent paths across different development environments.

## Code-Server Troubleshooting

### Q: Code-server shows "not available" error

This usually means:

1. The agent doesn't have code-server support enabled
2. Network connectivity issues
3. Agent is not properly configured

**Solution**: Reinstall the agent with code-server support, or check agent configuration.

### Q: Browser doesn't open automatically

This happens in headless environments or when display is not available.

**Solution**: Manually copy the provided URL (including the `?folder=` parameter) to your browser.

### Q: Plugin not detected in workspace

**Solution**: Ensure your directory contains a valid `config.yaml` file with plugin metadata:

```yaml
name: my-plugin
version: 1.0.0
description: My awesome plugin
entry_point: main.py
```

### Q: How does plugin encryption work?

When opening code-server with an agent, Synapse:

1. Detects if your workspace contains a plugin
2. Creates a ZIP archive of the plugin files
3. Encrypts the archive using AES-256 encryption
4. Securely transfers it to the agent
5. Decrypts and extracts it in the agent workspace

This ensures your plugin code is protected during transfer.

## Configuration

### Q: Where are configuration files stored?

- **Synapse Config**: `~/.synapse/devtools.yaml`
- **Code-Server Config**: `~/.config/code-server/config.yaml`

### Q: How do I reset my configuration?

```bash
# Remove configuration files
rm ~/.synapse/devtools.yaml
rm ~/.config/code-server/config.yaml

# Run configuration wizard
synapse config
```

### Q: What if I get "Invalid token (401)" error?

This means your API token is expired or invalid.

**Solution**:

1. Generate a new token from your Synapse backend
2. Run `synapse config` to update the token
3. Test connection with `synapse --dev-tools`

## Plugin Development

### Q: How do I create a new plugin?

Use the interactive plugin creator:

```bash
synapse
# Select "🔌 Plugin Management" → "Create new plugin"
```

This creates a complete plugin structure with examples and documentation.

### Q: How do I test plugins locally?

```bash
# Test with local script execution
synapse plugin run my_action '{"param": "value"}' --run-by script

# Test with agent execution
synapse plugin run my_action '{"param": "value"}' --run-by agent
```

Always test locally before publishing to ensure your plugin works correctly.

### Q: Plugin publishing fails with errors

Common issues:

1. **Missing dependencies**: Ensure `requirements.txt` includes all needed packages
2. **Syntax errors**: Test locally first with `--run-by script`
3. **Configuration errors**: Check `config.yaml` format and required fields
4. **Backend connectivity**: Ensure backend is accessible and token is valid

**Solution**: Use debug mode for detailed error information:

```bash
synapse plugin publish --debug
```
