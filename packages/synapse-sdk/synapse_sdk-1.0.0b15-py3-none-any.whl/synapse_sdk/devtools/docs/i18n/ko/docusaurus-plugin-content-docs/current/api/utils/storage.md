---
id: storage
title: Storage Providers
sidebar_position: 2
---

# Storage Providers

여러 클라우드 제공자를 지원하는 스토리지 추상화 레이어입니다.

## 지원되는 제공자

### Amazon S3

Amazon Simple Storage Service 통합입니다.

```python
from synapse_sdk.utils.storage.providers.s3 import S3Provider

provider = S3Provider(
    bucket="my-bucket",
    region="us-west-2"
)
```

### Google Cloud Storage

Google Cloud Storage 통합입니다.

```python
from synapse_sdk.utils.storage.providers.gcp import GCPProvider

provider = GCPProvider(
    bucket="my-bucket",
    project="my-project"
)
```

### SFTP

Secure File Transfer Protocol 지원입니다.

```python
from synapse_sdk.utils.storage.providers.sftp import SFTPProvider

provider = SFTPProvider(
    host="sftp.example.com",
    username="user"
)
```

## 사용법

```python
from synapse_sdk.utils.storage import get_storage

# URL에서 자동 제공자 감지
storage = get_storage("s3://my-bucket/file.csv")
local_path = storage.download()
```