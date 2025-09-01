---
id: models
title: Plugin Models
sidebar_position: 1
---

# Plugin Models

Core data models and structures for the plugin system.

## PluginRelease

Represents a specific version of a plugin.

```python
from synapse_sdk.plugins.models import PluginRelease

release = PluginRelease(plugin_path="./my-plugin")
```

### Properties

- `plugin`: Plugin code identifier
- `version`: Plugin version
- `code`: Combined plugin and version string
- `category`: Plugin category
- `name`: Human-readable plugin name
- `actions`: Available plugin actions

## PluginAction

Represents a plugin action execution request.

```python
from synapse_sdk.plugins.models import PluginAction

action = PluginAction(
    plugin="my-plugin",
    version="1.0.0",
    action="process",
    params={"input": "data"}
)
```

## Run

Execution context for plugin actions.

```python
def start(self):
    # Log messages
    self.run.log("Processing started")
    
    # Update progress
    self.run.set_progress(0.5)
    
    # Set metrics
    self.run.set_metrics({"processed": 100})
```