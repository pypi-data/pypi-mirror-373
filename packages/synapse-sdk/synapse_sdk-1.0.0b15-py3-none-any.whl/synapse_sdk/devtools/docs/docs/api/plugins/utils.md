---
id: utils
title: Plugin Utilities
sidebar_position: 3
---

# Plugin Utilities

Comprehensive utility functions for plugin development, configuration management, and action handling.

## Overview

The plugin utilities module (`synapse_sdk.plugins.utils`) provides a collection of functions for working with plugin configurations, managing actions, and handling plugin metadata. The utilities are organized into focused modules for better maintainability.

## Configuration Utilities

### read_plugin_config()

Read and parse plugin configuration from config.yaml file with enhanced error handling.

```python
from synapse_sdk.plugins.utils import read_plugin_config

# Read from specific plugin directory
config = read_plugin_config(plugin_path="./my-plugin")

# Read from current directory
config = read_plugin_config()
```

**Parameters:**

- `plugin_path` (optional): Path to plugin directory containing config.yaml

**Returns:** Dictionary containing parsed plugin configuration

**Raises:**

- `FileNotFoundError`: If config.yaml is not found
- `ValueError`: If config.yaml contains invalid YAML

### get_plugin_actions()

Get list of action names defined in a plugin configuration.

```python
from synapse_sdk.plugins.utils import get_plugin_actions

# From config dictionary
config = {'actions': {'train': {...}, 'inference': {...}}}
actions = get_plugin_actions(config=config)
# Returns: ['train', 'inference']

# From plugin path
actions = get_plugin_actions(plugin_path="./my-plugin")

# From current directory
actions = get_plugin_actions()
```

**Parameters:**

- `config` (optional): Plugin configuration dictionary
- `plugin_path` (optional): Path to plugin directory

**Returns:** List of action names

### get_action_config()

Retrieve configuration for a specific action within a plugin.

```python
from synapse_sdk.plugins.utils import get_action_config

# Get specific action configuration
action_config = get_action_config('train', plugin_path="./my-plugin")
# Returns: {'entrypoint': 'plugin.train.TrainAction', 'method': 'job'}

# With config dictionary
config = {'actions': {'train': {'entrypoint': 'plugin.train.TrainAction'}}}
action_config = get_action_config('train', config=config)
```

**Parameters:**

- `action_name`: Name of the action to retrieve
- `config` (optional): Plugin configuration dictionary
- `plugin_path` (optional): Path to plugin directory

**Returns:** Dictionary containing action configuration

### validate_plugin_config()

Validate plugin configuration structure and required fields.

```python
from synapse_sdk.plugins.utils import validate_plugin_config

config = {
    'name': 'My Plugin',
    'code': 'my-plugin',
    'version': '1.0.0',
    'category': 'neural_net',
    'actions': {'train': {'entrypoint': 'plugin.train.TrainAction'}}
}

is_valid = validate_plugin_config(config)  # Returns: True
```

**Validation Checks:**

- Required fields: `name`, `code`, `version`, `category`, `actions`
- Valid plugin category
- Proper actions structure
- Required entrypoints (except for REST API actions)

### get_plugin_metadata()

Extract metadata (name, version, description, etc.) from plugin configuration.

```python
from synapse_sdk.plugins.utils import get_plugin_metadata

metadata = get_plugin_metadata(plugin_path="./my-plugin")
# Returns: {
#     'name': 'My Plugin',
#     'code': 'my-plugin', 
#     'version': '1.0.0',
#     'category': 'neural_net',
#     'description': 'A custom ML plugin'
# }
```

## Action Utilities

### get_action_class()

Retrieve action class by category and action name from the registry.

```python
from synapse_sdk.plugins.utils import get_action_class

# Get action class for instantiation
TrainAction = get_action_class('neural_net', 'train')
action_instance = TrainAction(params, config)
```

### get_available_actions()

List all available actions for a specific plugin category.

```python
from synapse_sdk.plugins.utils import get_available_actions

actions = get_available_actions('neural_net')
# Returns: ['train', 'inference', 'test', 'deployment', 'gradio', 'tune']
```

### is_action_available()

Check if a specific action is available in a category.

```python
from synapse_sdk.plugins.utils import is_action_available

if is_action_available('neural_net', 'train'):
    print("Training action is available")
```

### get_action()

Create and configure a plugin action instance with parameters.

```python
from synapse_sdk.plugins.utils import get_action

# With dictionary parameters
params = {'dataset_path': '/data', 'epochs': 10}
action = get_action('train', params, plugin_path="./my-plugin")

# With JSON string parameters
params_json = '{"dataset_path": "/data", "epochs": 10}'
action = get_action('train', params_json, config=config)

# With file parameters
action = get_action('train', '/path/to/params.yaml')
```

## Registry Utilities

### get_plugin_categories()

Get list of all available plugin categories.

```python
from synapse_sdk.plugins.utils import get_plugin_categories

categories = get_plugin_categories()
# Returns: ['neural_net', 'export', 'upload', 'smart_tool', 
#           'post_annotation', 'pre_annotation', 'data_validation']
```

### is_valid_category()

Validate if a category name is valid.

```python
from synapse_sdk.plugins.utils import is_valid_category

if is_valid_category('neural_net'):
    print("Valid category")
```

### get_category_display_name()

Get human-readable display name for a category.

```python
from synapse_sdk.plugins.utils import get_category_display_name

display_name = get_category_display_name('neural_net')
# Returns: "Neural Net"

display_name = get_category_display_name('data_validation') 
# Returns: "Data Validation"
```

## Error Handling

All utility functions include comprehensive error handling with descriptive error messages:

```python
from synapse_sdk.plugins.utils import get_plugin_actions

try:
    actions = get_plugin_actions(plugin_path="./nonexistent")
except FileNotFoundError as e:
    print(f"Plugin config not found: {e}")
except ValueError as e:
    print(f"Invalid plugin config: {e}")
except KeyError as e:
    print(f"Missing required field: {e}")
```

## Usage Examples

### Complete Plugin Workflow

```python
from synapse_sdk.plugins.utils import (
    read_plugin_config,
    get_plugin_actions,
    get_action_config,
    validate_plugin_config,
    get_action_class
)

# 1. Read plugin configuration
config = read_plugin_config("./my-neural-net-plugin")

# 2. Validate configuration
if validate_plugin_config(config):
    print("✅ Plugin configuration is valid")

# 3. List available actions
actions = get_plugin_actions(config=config)
print(f"Available actions: {actions}")

# 4. Get specific action configuration
train_config = get_action_config('train', config=config)
print(f"Train entrypoint: {train_config['entrypoint']}")

# 5. Create action instance
TrainAction = get_action_class(config['category'], 'train')
action = TrainAction(
    params={'dataset_path': '/data', 'epochs': 10},
    plugin_config=config
)
```

### Plugin Development Helper

```python
from synapse_sdk.plugins.utils import (
    get_plugin_categories,
    get_available_actions,
    is_action_available
)

# Check available categories
categories = get_plugin_categories()
print("Available plugin categories:")
for category in categories:
    print(f"  - {category}")
    
    # List actions for each category
    actions = get_available_actions(category)
    for action in actions:
        print(f"    - {action}")

# Verify action availability
if is_action_available('neural_net', 'train'):
    print("✅ Train action is available for neural_net plugins")
```

## Migration from Legacy API

The new utilities maintain backward compatibility while providing enhanced functionality:

```python
# Legacy (still supported)
from synapse_sdk.plugins.utils import read_plugin_config

# New enhanced API (recommended)
from synapse_sdk.plugins.utils import (
    read_plugin_config,
    get_plugin_actions,
    validate_plugin_config
)
```

## Best Practices

1. **Error Handling**: Always wrap utility calls in try-catch blocks
2. **Configuration Validation**: Validate configs before using them
3. **Path Handling**: Use absolute paths when possible
4. **Action Verification**: Check action availability before instantiation
5. **Type Safety**: Use the provided type hints for better IDE support
