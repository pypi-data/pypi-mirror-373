---
id: storage
title: Storage Providers
sidebar_position: 2
---

# Storage Providers

Storage abstraction layer supporting multiple cloud providers.

## Supported Providers

### Amazon S3
Amazon Simple Storage Service integration.

```python
from synapse_sdk.utils.storage.providers.s3 import S3Provider

provider = S3Provider(
    bucket="my-bucket",
    region="us-west-2"
)
```

### Google Cloud Storage
Google Cloud Storage integration.

```python
from synapse_sdk.utils.storage.providers.gcp import GCPProvider

provider = GCPProvider(
    bucket="my-bucket",
    project="my-project"
)
```

### SFTP
Secure File Transfer Protocol support.

```python
from synapse_sdk.utils.storage.providers.sftp import SFTPProvider

provider = SFTPProvider(
    host="sftp.example.com",
    username="user"
)
```

## Usage

```python
from synapse_sdk.utils.storage import get_storage

# Automatic provider detection from URL
storage = get_storage("s3://my-bucket/file.csv")
local_path = storage.download()
```