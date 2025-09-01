---
id: types
title: Custom Types
sidebar_position: 3
---

# Custom Types

Custom types and Pydantic fields used throughout the SDK.

## FileField

Custom Pydantic field for handling file URLs with automatic download.

```python
from synapse_sdk.types import FileField
from pydantic import BaseModel

class MyParams(BaseModel):
    input_file: FileField  # Automatically downloads files

def process(params: MyParams):
    file_path = params.input_file  # Local file path
    # Process the file...
```

### Features

- Automatic file download from URLs
- Temporary file management
- Support for various file formats
- Validation of file existence

## Usage Examples

```python
# In plugin parameters
class ProcessParams(BaseModel):
    data_file: FileField
    config_file: FileField = None  # Optional file

# The FileField automatically:
# 1. Downloads the file from URL
# 2. Validates file existence
# 3. Returns local file path
# 4. Cleans up temporary files
```

## Type Validation

Custom validators for ensuring type safety across the SDK.