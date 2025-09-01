---
id: ray
title: RayClient
sidebar_position: 4
---

# RayClient

Apache Ray 클러스터 관리 및 모니터링 기능을 위한 클라이언트입니다.

## 개요

`RayClientMixin`은 작업 관리, 실시간 로그 스트리밍, 노드 모니터링, Ray Serve 애플리케이션 제어를 포함한 포괄적인 Ray 클러스터 작업을 제공합니다. Ray 전용 기능으로 `BaseClient`를 확장하는 mixin 클래스로 설계되었습니다.

## 주요 기능

- **Job 라이프사이클 관리**: Ray 작업 생성, 모니터링 및 관리
- **실시간 로그 스트리밍**: WebSocket 및 HTTP 기반 로그 테일링
- **노드 및 태스크 모니터링**: 클러스터 리소스 및 태스크 실행 모니터링
- **Ray Serve 통합**: Ray Serve 애플리케이션 배포 및 관리
- **강력한 오류 처리**: 입력 유효성 검사 및 정제된 오류 메시지
- **리소스 관리**: 자동 정리 및 연결 추적

## Constructor

```python
# RayClientMixin은 일반적으로 mixin으로 사용됩니다
class RayClient(RayClientMixin):
    def __init__(self, base_url: str, timeout: dict = None):
        super().__init__(base_url, timeout)
```

### Parameters

- `base_url` (str): Ray 클러스터 대시보드 URL (예: "http://ray-head:8265")
- `timeout` (dict, 선택사항): 연결 및 읽기 timeout 설정

## 사용법

```python
from synapse_sdk.clients.agent.ray import RayClientMixin
from synapse_sdk.clients.base import BaseClient

class RayClient(RayClientMixin, BaseClient):
    pass

client = RayClient(base_url="http://ray-head:8265")

# 모든 작업 나열
jobs = client.list_jobs()

# 특정 작업 세부정보 가져오기
job = client.get_job('job-12345')

# 실시간으로 로그 스트리밍
for log_line in client.tail_job_logs('job-12345'):
    print(log_line.strip())
```

## Job 작업

### `get_job(pk)`

특정 작업에 대한 세부정보를 검색합니다.

```python
job = client.get_job('job-12345')
print(f"Job 상태: {job['status']}")
```

### `list_jobs()`

Ray 클러스터의 모든 작업을 나열합니다.

```python
jobs = client.list_jobs()
for job in jobs['results']:
    print(f"Job {job['id']}: {job['status']}")
```

### `list_job_logs(pk)`

작업에 대한 정적 로그 항목을 가져옵니다.

```python
logs = client.list_job_logs('job-12345')
```

## 실시간 로그 스트리밍

### `tail_job_logs(pk, stream_timeout=10, protocol='stream')`

WebSocket 또는 HTTP 프로토콜을 사용하여 작업 로그를 스트리밍합니다.

```python
# HTTP 스트리밍 (기본값, 호환성 높음)
for log_line in client.tail_job_logs('job-12345', protocol='stream'):
    print(log_line.strip())

# WebSocket 스트리밍 (낮은 지연시간)
for log_line in client.tail_job_logs('job-12345', protocol='websocket'):
    print(log_line.strip())

# 사용자 정의 timeout으로
for log_line in client.tail_job_logs('job-12345', stream_timeout=30):
    if 'ERROR' in log_line:
        break
```

### `websocket_tail_job_logs(pk, stream_timeout=10)`

가장 낮은 지연시간을 위해 WebSocket을 통해 로그를 스트리밍합니다.

```python
try:
    for log_line in client.websocket_tail_job_logs('job-12345'):
        print(log_line.strip())
        if 'COMPLETED' in log_line:
            break
except ClientError as e:
    print(f"WebSocket 스트리밍 실패: {e}")
```

### `stream_tail_job_logs(pk, stream_timeout=10)`

HTTP chunked transfer encoding을 통해 로그를 스트리밍합니다.

```python
for log_line in client.stream_tail_job_logs('job-12345', stream_timeout=60):
    if 'FAILED' in log_line:
        print(f"Job 실패: {log_line}")
        break
```

## 노드 작업

### `get_node(pk)`

특정 클러스터 노드에 대한 세부정보를 가져옵니다.

```python
node = client.get_node('node-abc123')
print(f"노드 상태: {node['alive']}")
```

### `list_nodes()`

Ray 클러스터의 모든 노드를 나열합니다.

```python
nodes = client.list_nodes()
for node in nodes['results']:
    print(f"노드 {node['node_id']}: {node['state']}")
```

## 태스크 작업

### `get_task(pk)`

특정 태스크에 대한 세부정보를 검색합니다.

```python
task = client.get_task('task-xyz789')
```

### `list_tasks()`

클러스터의 모든 태스크를 나열합니다.

```python
tasks = client.list_tasks()
```

## Ray Serve 작업

### `get_serve_application(pk)`

Ray Serve 애플리케이션에 대한 세부정보를 가져옵니다.

```python
app = client.get_serve_application('app-123')
print(f"애플리케이션 상태: {app['status']}")
```

### `list_serve_applications()`

모든 Ray Serve 애플리케이션을 나열합니다.

```python
apps = client.list_serve_applications()
```

### `delete_serve_application(pk)`

Ray Serve 애플리케이션을 삭제합니다.

```python
client.delete_serve_application('app-123')
```

## 오류 처리

모든 메서드에는 특정 `ClientError` 예외와 함께 강력한 오류 처리가 포함됩니다:

```python
from synapse_sdk.clients.exceptions import ClientError

try:
    for log_line in client.tail_job_logs('invalid-job'):
        print(log_line)
except ClientError as e:
    if e.status == 400:
        print("잘못된 작업 ID 또는 매개변수")
    elif e.status == 404:
        print("작업을 찾을 수 없음")
    elif e.status == 503:
        print("Ray 클러스터 연결 실패")
    else:
        print(f"예상치 못한 오류: {e}")
```

### 일반적인 오류 코드

- **400**: 잘못된 매개변수 (job ID, timeout, protocol)
- **404**: 리소스를 찾을 수 없음 (job, node, task, application)
- **408**: 연결 또는 읽기 timeout
- **429**: 스트림 제한 초과
- **500**: WebSocket 라이브러리 사용 불가 또는 내부 오류
- **503**: Ray 클러스터 연결 실패

## 리소스 관리

RayClient에는 자동 리소스 관리가 포함됩니다:

- **Thread Pool**: 동시 작업을 위한 5개 작업자 스레드
- **연결 추적**: 활성 연결을 위한 WeakSet
- **스트림 제한**: 메모리 고갈 방지
- **자동 정리**: 소멸 시 리소스 정리

### 스트림 제한

로그 스트리밍을 위한 기본 제한:

- 최대 메시지: 10,000
- 최대 라인: 50,000
- 최대 바이트: 50MB
- 최대 메시지 크기: 10KB
- Queue 크기: 1,000

## 모범 사례

### 1. 프로토콜 선택

```python
# 사용 가능한 경우 가장 낮은 지연시간을 위해 WebSocket 사용
try:
    logs = client.tail_job_logs(job_id, protocol='websocket')
except ClientError:
    # HTTP 스트리밍으로 폴백
    logs = client.tail_job_logs(job_id, protocol='stream')
```

### 2. Timeout 관리

```python
# 장기 실행 작업에 적절한 timeout 사용
for log_line in client.tail_job_logs(job_id, stream_timeout=300):
    process_log_line(log_line)
```

### 3. 오류 복구

```python
import time

def robust_log_streaming(client, job_id, max_retries=3):
    for attempt in range(max_retries):
        try:
            for log_line in client.tail_job_logs(job_id):
                yield log_line
            break
        except ClientError as e:
            if e.status == 503 and attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # 지수 백오프
                continue
            raise
```

### 4. 리소스 정리

```python
# 적절한 정리를 위한 컨텍스트 매니저
class RayClientContext:
    def __init__(self, base_url):
        self.client = RayClient(base_url)

    def __enter__(self):
        return self.client

    def __exit__(self, exc_type, exc_val, exc_tb):
        # RayClient.__del__()에 의해 자동으로 정리 처리
        pass

with RayClientContext("http://ray-head:8265") as client:
    for log_line in client.tail_job_logs('job-12345'):
        print(log_line.strip())
```

## 스레드 안전성

RayClient는 적절한 스레드 안전 메커니즘을 통해 동시 사용을 위해 설계되었습니다:

- 백그라운드 작업을 위한 스레드 풀
- 연결 추적을 위한 WeakSet
- 적절한 리소스 정리 메커니즘

## 참고

- [AgentClient](./agent.md) - Agent 전용 작업을 위한 클라이언트
- [BaseClient](./base.md) - 기본 클라이언트 구현
- [Network Utilities](../utils/network.md) - 스트리밍 및 유효성 검사 유틸리티