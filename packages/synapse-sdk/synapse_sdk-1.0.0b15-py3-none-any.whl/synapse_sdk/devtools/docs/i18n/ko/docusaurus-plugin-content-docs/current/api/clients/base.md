---
id: base
title: BaseClient
sidebar_position: 3
---

# BaseClient

모든 Synapse SDK 클라이언트의 기본 클래스입니다.

## 개요

`BaseClient`는 다른 모든 클라이언트에서 사용하는 HTTP 작업, 오류 처리 및 요청 관리를 위한 공통 기능을 제공합니다.

## 기능

- 재시도 로직이 있는 HTTP 요청 처리
- 자동 timeout 관리
- 파일 업로드/다운로드 기능
- Pydantic 모델 유효성 검사
- 연결 풀링

## 사용법

```python
from synapse_sdk.clients.base import BaseClient

# BaseClient는 일반적으로 직접 사용되지 않습니다
# 대신 BackendClient 또는 AgentClient를 사용하세요
```

## 참고

- [BackendClient](./backend.md) - 메인 클라이언트 구현
- [AgentClient](./agent.md) - Agent 전용 작업