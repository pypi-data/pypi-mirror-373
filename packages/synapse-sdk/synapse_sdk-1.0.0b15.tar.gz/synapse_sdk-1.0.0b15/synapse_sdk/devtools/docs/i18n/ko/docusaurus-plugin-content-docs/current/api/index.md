---
id: index
title: API 참조
sidebar_position: 1
---

# API 참조

Synapse SDK 클래스 및 함수에 대한 완전한 참조 문서입니다.

## 개요

Synapse SDK API는 다음 주요 모듈로 구성됩니다:

### [클라이언트](./clients/backend.md)
백엔드 서비스 및 에이전트와 상호작용하기 위한 클라이언트 클래스들.

- **[BackendClient](./clients/backend.md)** - 백엔드 작업을 위한 메인 클라이언트
- **[AgentClient](./clients/agent.md)** - 에이전트 특정 작업을 위한 클라이언트
- **[RayClient](./clients/ray.md)** - Ray 클러스터 관리 및 모니터링을 위한 클라이언트
- **[BaseClient](./clients/base.md)** - 모든 클라이언트의 기본 클래스

핵심 플러그인 시스템 컴포넌트들.

### [유틸리티](./utils/file.md)
도우미 함수 및 유틸리티들.

- **[파일 유틸](./utils/file.md)** - 파일 작업 및 처리
- **[네트워크](./utils/network.md)** - 스트리밍, 검증 및 연결 관리
- **[스토리지](./utils/storage.md)** - 스토리지 제공자들 (S3, GCS, SFTP)
- **[타입](./utils/types.md)** - 커스텀 타입 및 필드

## 빠른 참조

### 클라이언트 생성

```python
from synapse_sdk.clients.backend import BackendClient

client = BackendClient(
    base_url="https://api.synapse.sh",
    api_token="your-api-token"
)
```

### 플러그인 실행

### 플러그인 액션 생성

## 타입 어노테이션

## 파일 처리