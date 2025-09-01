---
id: backend
title: BackendClient
sidebar_position: 1
---

# BackendClient

Synapse backend API와 상호작용하기 위한 메인 클라이언트입니다.

## 개요

`BackendClient`는 데이터 관리, 플러그인 실행, 어노테이션, 머신러닝 워크플로우를 포함한 모든 backend 작업에 대한 포괄적인 액세스를 제공합니다. 여러 전문화된 mixin의 기능을 집계합니다.

## Constructor

```python
BackendClient(
    base_url: str,
    api_token: str = None,
    agent_token: str = None,
    timeout: dict = None
)
```

### Parameters

- **base_url** (`str`): Synapse backend API의 기본 URL
- **api_token** (`str`, 선택사항): API 인증 토큰. `SYNAPSE_API_TOKEN` 환경변수로도 설정 가능
- **agent_token** (`str`, 선택사항): Agent 인증 토큰. `SYNAPSE_AGENT_TOKEN` 환경변수로도 설정 가능
- **timeout** (`dict`, 선택사항): 사용자 정의 timeout 설정. 기본값은 `{'connect': 5, 'read': 30}`

### 예제

```python
from synapse_sdk.clients.backend import BackendClient

# 명시적 토큰으로 클라이언트 생성
client = BackendClient(
    base_url="https://api.synapse.sh",
    api_token="your-api-token"
)

# 또는 환경변수 사용
import os
os.environ['SYNAPSE_API_TOKEN'] = "your-api-token"
client = BackendClient(base_url="https://api.synapse.sh")
```

## 참고

- [AgentClient](./agent.md) - Agent 전용 작업을 위한 클라이언트
- [BaseClient](./base.md) - 기본 클라이언트 구현