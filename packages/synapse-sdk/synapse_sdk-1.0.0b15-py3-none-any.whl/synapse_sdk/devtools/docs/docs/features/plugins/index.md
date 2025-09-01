---
id: plugins
title: Plugin System
sidebar_position: 2
---

# Plugin System

The Synapse SDK provides a comprehensive plugin system for building and managing ML plugins across different categories and execution methods. The plugin system enables modular, reusable components that can be distributed and executed in various environments.

## Overview

The plugin system is built around the concept of **actions** - discrete operations that can be packaged, distributed, and executed in different contexts. Each plugin belongs to a specific category and can support multiple actions.

### Key Features

- **🔌 Modular Architecture**: Plugins are self-contained with their own dependencies and configuration
- **⚡ Multiple Execution Methods**: Support for Jobs, Tasks, and REST API endpoints
- **📦 Distributed Execution**: Built for scalable, distributed computing
- **🛠️ Template System**: Cookiecutter-based scaffolding for rapid plugin development
- **📊 Progress Tracking**: Built-in logging, metrics, and progress monitoring
- **🔄 Dynamic Loading**: Runtime plugin discovery and registration

## Plugin Categories

The SDK organizes plugins into specific categories, each designed for different aspects of ML workflows:

### 1. Neural Networks (`neural_net`)

ML model training, inference, and deployment operations.

**Available Actions:**
- `deployment` - Deploy models to production environments
- `gradio` - Create interactive web interfaces for models
- `inference` - Run model predictions on data
- `test` - Validate model performance and accuracy
- `train` - Train ML models with custom datasets
- `tune` - Hyperparameter optimization and model tuning

**Use Cases:**
- Training computer vision models
- Deploying models as web services
- Running batch inference on datasets
- Creating interactive model demos

### 2. Export (`export`)

Data export and transformation operations.

**Available Actions:**
- `export` - Export data in various formats and destinations

**Use Cases:**
- Converting datasets to different formats
- Exporting processed data to cloud storage
- Creating data packages for distribution

### 3. Upload (`upload`)

File and data upload functionality with support for various storage backends.

**Available Actions:**
- `upload` - Upload files to storage providers

**Use Cases:**
- Uploading datasets to cloud storage
- Backing up processed data
- Sharing data between team members

### 4. Smart Tools (`smart_tool`)

Intelligent automation tools powered by AI.

**Available Actions:**
- `auto_label` - Automated data labeling and annotation

**Use Cases:**
- Pre-labeling datasets with AI models
- Quality assurance for manual annotations
- Accelerating annotation workflows

### 5. Pre-annotation (`pre_annotation`)

Data preparation and processing before annotation.

**Available Actions:**
- `pre_annotation` - Prepare data for annotation workflows
- `to_task` - Convert data to annotation tasks

**Use Cases:**
- Data preprocessing and filtering
- Creating annotation tasks from raw data
- Setting up annotation workflows

### 6. Post-annotation (`post_annotation`)

Data processing and validation after annotation.

**Available Actions:**
- `post_annotation` - Process completed annotations

**Use Cases:**
- Validating annotation quality
- Post-processing annotated data
- Generating training datasets from annotations

### 7. Data Validation (`data_validation`)

Data quality checks and validation operations.

**Available Actions:**
- `validation` - Perform data quality and integrity checks

**Use Cases:**
- Validating dataset integrity
- Checking annotation consistency
- Quality assurance workflows

## Execution Methods

Plugins support three different execution methods depending on the use case:

### Job Execution

**Job-based execution** for long-running, distributed processing tasks.

- Best for: Training models, processing large datasets
- Features: Distributed execution, resource management, fault tolerance
- Monitoring: Full job lifecycle tracking and logging

### Task Execution

**Task-based execution** for simple, short-running operations.

- Best for: Quick data processing, validation checks
- Features: Lightweight execution, fast startup
- Monitoring: Basic progress tracking

### REST API Execution

**Serve-based execution** for web API endpoints.

- Best for: Real-time inference, interactive applications
- Features: HTTP endpoints, auto-scaling, load balancing
- Monitoring: Request/response logging, performance metrics

## Plugin Architecture

### Core Components

#### Plugin Models

**PluginRelease Class** (`synapse_sdk/plugins/models.py:14`)
- Manages plugin metadata and configuration
- Handles versioning and checksums
- Provides runtime environment setup

**Run Class** (`synapse_sdk/plugins/models.py:98`)
- Manages plugin execution instances
- Provides logging and progress tracking
- Handles backend communication

#### Action Base Class

**Action Class** (`synapse_sdk/plugins/categories/base.py:19`)
- Unified interface for all plugin actions
- Parameter validation with Pydantic models
- Built-in logging and error handling
- Runtime environment management

#### Template System

**Cookiecutter Templates** (`synapse_sdk/plugins/templates/`)
- Standardized plugin scaffolding
- Category-specific templates
- Automated project setup with proper structure

### Plugin Structure

Each plugin follows a standardized structure:

```
synapse-{plugin-code}-plugin/
├── config.yaml              # Plugin metadata and configuration
├── plugin/                  # Source code directory
│   ├── __init__.py
│   ├── {action1}.py        # Action implementations
│   └── {action2}.py
├── requirements.txt         # Python dependencies
├── pyproject.toml          # Package configuration
└── README.md               # Plugin documentation
```

### Configuration File (`config.yaml`)

```yaml
# Plugin metadata
code: "my-plugin"
name: "My Custom Plugin"
version: "1.0.0"
category: "neural_net"
description: "A custom ML plugin"

# Package management
package_manager: "pip"  # or "uv"

# Action definitions
actions:
  train:
    entrypoint: "plugin.train.TrainAction"
    method: "job"
  inference:
    entrypoint: "plugin.inference.InferenceAction"
    method: "restapi"
```

## Creating Plugins

### 1. Generate Plugin Template

Use the CLI to create a new plugin from templates:

```bash
synapse plugin create
```

This will prompt for:
- Plugin code (unique identifier)
- Plugin name and description
- Category selection
- Required actions

### 2. Implement Actions

Each action inherits from the base `Action` class:

```python
# plugin/train.py
from synapse_sdk.plugins.categories.neural_net import TrainAction as BaseTrainAction
from pydantic import BaseModel

class TrainParams(BaseModel):
    dataset_path: str
    epochs: int = 10
    learning_rate: float = 0.001

class TrainAction(BaseTrainAction):
    name = "train"
    params_model = TrainParams
    
    def start(self):
        # Access validated parameters
        dataset_path = self.params['dataset_path']
        epochs = self.params['epochs']
        
        # Log progress
        self.run.log_message("Starting training...")
        
        # Your training logic here
        for epoch in range(epochs):
            # Update progress
            self.run.set_progress(epoch + 1, epochs, "training")
            
            # Training step
            loss = train_epoch(dataset_path)
            
            # Log metrics
            self.run.set_metrics({"loss": loss}, "training")
        
        self.run.log_message("Training completed!")
        return {"status": "success", "final_loss": loss}
```

### 3. Configure Actions

Define actions in `config.yaml`:

```yaml
actions:
  train:
    entrypoint: "plugin.train.TrainAction"
    method: "job"
    description: "Train a neural network model"
```

### 4. Package and Publish

```bash
# Test locally
synapse plugin run train --debug

# Package for distribution
synapse plugin publish
```

## Running Plugins

### Command Line Interface

```bash
# Run a plugin action
synapse plugin run {action} {params}

# With specific plugin
synapse plugin run train '{"dataset_path": "/data/images", "epochs": 20}' --plugin my-plugin@1.0.0

# Debug mode (use local code)
synapse plugin run train '{"dataset_path": "/data/images"}' --debug

# Background job
synapse plugin run train '{"dataset_path": "/data/images"}' --job-id my-training-job
```

### Programmatic Usage

```python
from synapse_sdk.plugins.utils import get_action_class

# Get action class by category and name
ActionClass = get_action_class("neural_net", "train")

# Create and run action
action = ActionClass(
    params={"dataset_path": "/data/images", "epochs": 10},
    plugin_config=plugin_config,
    envs=env_vars
)

result = action.run_action()
```

## Development Workflow

### 1. Local Development

```bash
# Create plugin
synapse plugin create

# Develop and test locally
cd synapse-my-plugin-plugin
synapse plugin run action-name --debug

# Use development server for REST APIs
synapse plugin run serve --debug
```

### 2. Testing

```bash
# Run plugin tests
pytest plugin/test_*.py

# Integration testing with distributed computing
synapse plugin run action-name --debug --job-id test-job
```

### 3. Deployment

```bash
# Package plugin
synapse plugin publish

# Deploy to cluster
synapse plugin run action-name --job-id production-job
```

## Advanced Features

### Custom Progress Categories

```python
class MyAction(Action):
    progress_categories = {
        "preprocessing": "Data preprocessing",
        "training": "Model training", 
        "validation": "Model validation"
    }
    
    def start(self):
        # Update different progress categories
        self.run.set_progress(50, 100, "preprocessing")
        self.run.set_progress(10, 50, "training")
```

### Custom Metrics

```python
def start(self):
    # Log custom metrics
    self.run.set_metrics({
        "accuracy": 0.95,
        "loss": 0.1,
        "f1_score": 0.92
    }, "validation")
```

### Runtime Environment Customization

```python
def get_runtime_env(self):
    env = super().get_runtime_env()
    
    # Add custom environment variables
    env['env_vars']['CUSTOM_VAR'] = 'value'
    
    # Add additional packages
    env['pip']['packages'].append('custom-package==1.0.0')
    
    return env
```

### Parameter Validation

```python
from pydantic import BaseModel, validator
from typing import Literal

class TrainParams(BaseModel):
    model_type: Literal["cnn", "transformer", "resnet"]
    dataset_path: str
    batch_size: int = 32
    
    @validator('batch_size')
    def validate_batch_size(cls, v):
        if v <= 0 or v > 512:
            raise ValueError('Batch size must be between 1 and 512')
        return v
```

## Best Practices

### 1. Plugin Design

- **Single Responsibility**: Each action should have a clear, focused purpose
- **Parameterization**: Make actions configurable through parameters
- **Error Handling**: Implement robust error handling and validation
- **Documentation**: Provide clear documentation and examples

### 2. Performance

- **Resource Management**: Use appropriate resource allocation for jobs
- **Progress Tracking**: Provide meaningful progress updates for long operations
- **Logging**: Log important events and errors for debugging
- **Memory Management**: Handle large datasets efficiently

### 3. Testing

- **Unit Tests**: Test individual action logic
- **Integration Tests**: Test with distributed execution environment
- **Parameter Validation**: Test edge cases and error conditions
- **Performance Tests**: Validate execution time and resource usage

### 4. Security

- **Input Validation**: Validate all parameters and inputs
- **File Access**: Restrict file system access appropriately
- **Dependencies**: Keep dependencies updated and secure
- **Secrets**: Never log sensitive information

## Monitoring and Debugging

### Plugin Execution Logs

```python
# In your action
self.run.log_message("Processing started", "INFO")
self.run.log_message("Warning: low memory", "WARNING") 
self.run.log_message("Error occurred", "ERROR")

# With structured data
self.run.log("model_checkpoint", {
    "epoch": 10,
    "accuracy": 0.95,
    "checkpoint_path": "/models/checkpoint_10.pth"
})
```

### Progress Monitoring

```python
# Simple progress
self.run.set_progress(current=50, total=100)

# Categorized progress
self.run.set_progress(current=30, total=100, category="training")
self.run.set_progress(current=20, total=50, category="validation")
```

### Metrics Collection

```python
# Training metrics
self.run.set_metrics({
    "epoch": 10,
    "train_loss": 0.1,
    "train_accuracy": 0.95,
    "learning_rate": 0.001
}, "training")

# Performance metrics
self.run.set_metrics({
    "inference_time": 0.05,
    "throughput": 200,
    "memory_usage": 1024
}, "performance")
```

The plugin system provides a powerful foundation for building scalable, distributed ML workflows. By following the established patterns and best practices, you can create robust plugins that integrate seamlessly with the Synapse ecosystem.