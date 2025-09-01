---
id: categories
title: Plugin Categories
sidebar_position: 2
---

# Plugin Categories

Available plugin categories in the Synapse SDK.

## Available Categories

### NEURAL_NET
Machine learning model operations including training, inference, and deployment.

### EXPORT
Data export and transformation operations.

### UPLOAD
File and data upload functionality.

### SMART_TOOL
Intelligent automation tools and utilities.

### POST_ANNOTATION
Post-processing workflows after data annotation.

### PRE_ANNOTATION
Pre-processing workflows before data annotation.

### DATA_VALIDATION
Data quality checks and validation operations.

## Usage

```python
from synapse_sdk.plugins.categories.smart_tool import register_action, Action

@register_action("my_action")
class MyAction(Action):
    category = "SMART_TOOL"
    # Implementation...
```