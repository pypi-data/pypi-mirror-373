---
id: agent
title: AgentClient
sidebar_position: 2
---

# AgentClient

Agent 전용 작업 및 분산 실행을 위한 클라이언트입니다.

## 개요

`AgentClient`는 플러그인 실행, 작업 관리, 분산 컴퓨팅 통합을 포함한 agent 작업에 대한 액세스를 제공합니다.

## Constructor

```python
AgentClient(
    base_url: str,
    agent_token: str = None,
    timeout: dict = None
)
```

## 사용법

```python
from synapse_sdk.clients.agent import AgentClient

client = AgentClient(
    base_url="https://api.synapse.sh",
    agent_token="your-agent-token"
)
```

## Methods

곧 제공 예정 - AgentClient 메서드에 대한 상세 API 문서.

## 참고

- [BackendClient](./backend.md) - Backend 작업을 위한 클라이언트
- [BaseClient](./base.md) - 기본 클라이언트 구현