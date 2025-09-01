---
id: quickstart
title: Quickstart Guide
sidebar_position: 3
---

# Quickstart Guide

Get up and running with Synapse SDK in minutes.

## Interactive CLI

Launch the Synapse CLI to access all features through an interactive menu:

```bash
synapse
```

This opens the main menu with options for:

- 🌐 **Dev Tools**: Web-based dashboard for agent and job management
- 💻 **Code-Server IDE**: Web-based VS Code for plugin development
- ⚙️ **Configuration**: Setup backend connections and agents
- 🔌 **Plugin Management**: Create, test, and publish plugins

## Quick Commands

For faster access to specific features:

```bash
# Start development tools immediately
synapse --dev-tools

# Configure backend and agents
synapse config

# Open code editing environment
synapse code-server

# Create a new plugin
synapse plugin create
```

## Your First Plugin

1. **Create a plugin**:

   ```bash
   synapse
   # Select "🔌 Plugin Management" → "Create new plugin"
   ```

2. **Edit in Code-Server**:

   ```bash
   synapse
   # Select "💻 Open Code-Server IDE"
   ```

3. **Test locally**:

   ```bash
   synapse plugin run my_action '{"param": "value"}' --run-by script
   ```

4. **Publish to backend**:

   ```bash
   synapse
   # Select "🔌 Plugin Management" → "Publish plugin"
   ```

## Next Steps

- Read the complete [CLI Usage Guide](./cli-usage.md)
- Learn about [Core Concepts](./concepts/index.md)
- Explore the [API Reference](./api/index.md)
- Check [Frequently Asked Questions](./faq.md)
