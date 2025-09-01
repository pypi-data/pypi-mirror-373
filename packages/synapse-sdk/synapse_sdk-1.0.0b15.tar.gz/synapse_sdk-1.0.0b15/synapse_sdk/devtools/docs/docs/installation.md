---
id: installation
title: Installation & Setup
sidebar_position: 2
---

# Installation & Setup

Get started with Synapse SDK in minutes.

## Prerequisites

Before installing Synapse SDK, ensure you have:

- **Python 3.10 or higher** installed

## Installation Methods

### Install from PyPI

The easiest way to install Synapse SDK is via pip:

```bash
pip install synapse-sdk
```

### Install with Optional Dependencies

For additional features, install with extras:

```bash
# Install with all dependencies (distributed computing, optimization libraries)
pip install synapse-sdk[all]

# Install with dashboard dependencies (FastAPI, Uvicorn)
pip install synapse-sdk[devtools]

# Install both
pip install "synapse-sdk[all,devtools]"
```

### Install from Source

To get the latest development version:

```bash
git clone https://github.com/datamaker/synapse-sdk.git
cd synapse-sdk
pip install -e .

# With optional dependencies
pip install -e ".[all,devtools]"
```

## Verify Installation

After installation, verify everything is working:

```bash
# Check version
synapse --version

# Run interactive CLI
synapse

# Run with devtools
synapse --dev-tools
```

## Troubleshooting

### Common Issues

1. **ImportError: No module named 'synapse_sdk'**
   - Ensure you've activated your virtual environment
   - Check Python path: `python -c "import sys; print(sys.path)"`

2. **Connection timeout to backend**
   - Verify your API token is correct
   - Check network connectivity
   - Ensure backend URL is accessible

### Getting Help

If you encounter issues:

1. Check the [Troubleshooting Guide](./troubleshooting.md)
2. Search [GitHub Issues](https://github.com/datamaker/synapse-sdk/issues)
3. Join our [Discord Community](https://discord.gg/synapse-sdk)

## Next Steps

- Follow the [Quickstart Guide](./quickstart.md)
- Learn about [Core Concepts](./concepts/index.md)