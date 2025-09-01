---
id: network
title: Network Utilities
sidebar_position: 4
---

# Network Utilities

스트리밍, 유효성 검사 및 연결 관리를 위한 포괄적인 네트워킹 유틸리티입니다.

## 개요

`synapse_sdk.utils.network` 모듈은 Ray 및 기타 클라이언트에서 안전하고 강력한 스트리밍 작업 및 입력 유효성 검사를 위해 사용하는 필수 네트워킹 구성 요소를 제공합니다.

## StreamLimits

리소스 고갈을 방지하기 위한 스트리밍 작업 제한을 위한 구성 클래스입니다.

### Constructor

```python
from synapse_sdk.utils.network import StreamLimits

limits = StreamLimits(
    max_messages=10000,
    max_lines=50000,
    max_bytes=50 * 1024 * 1024,  # 50MB
    max_message_size=10240,      # 10KB
    queue_size=1000,
    exception_queue_size=10
)
```

### Parameters

- `max_messages` (int): 처리할 최대 메시지 수 (기본값: 10,000)
- `max_lines` (int): 스트리밍할 최대 라인 수 (기본값: 50,000)
- `max_bytes` (int): 처리할 최대 총 바이트 (기본값: 50MB)
- `max_message_size` (int): 메시지당 최대 크기 (기본값: 10KB)
- `queue_size` (int): 메시지 버퍼링을 위한 내부 큐 크기 (기본값: 1,000)
- `exception_queue_size` (int): 예외 처리를 위한 큐 크기 (기본값: 10)

### 사용법

```python
# 대용량 스트리밍을 위한 사용자 정의 제한
custom_limits = StreamLimits(
    max_messages=50000,
    max_lines=100000,
    max_bytes=100 * 1024 * 1024  # 100MB
)

# 스트림 매니저와 함께 사용
websocket_manager = WebSocketStreamManager(thread_pool, custom_limits)
```

## WebSocketStreamManager

자동 오류 처리 및 리소스 정리를 통한 실시간 로그 스트리밍을 위해 WebSocket 연결을 관리합니다.

### Constructor

```python
from synapse_sdk.utils.network import WebSocketStreamManager
from concurrent.futures import ThreadPoolExecutor

thread_pool = ThreadPoolExecutor(max_workers=5)
limits = StreamLimits()
manager = WebSocketStreamManager(thread_pool, limits)
```

### Methods

#### `stream_logs(ws_url, headers, timeout, context)`

WebSocket 엔드포인트에서 로그를 스트리밍합니다.

```python
# 오류 처리가 있는 로그 스트리밍
try:
    for log_line in manager.stream_logs(
        ws_url="wss://ray-cluster:8265/logs/ws/",
        headers={"Authorization": "Bearer token"},
        timeout=30.0,
        context="job job-12345"
    ):
        print(log_line.strip())
except ClientError as e:
    print(f"스트리밍 실패: {e}")
```

### 오류 처리

- **500**: WebSocket 라이브러리 사용 불가
- **503**: 연결 실패
- **408**: 연결 timeout
- **429**: 스트림 제한 초과

## HTTPStreamManager

신뢰할 수 있는 로그 스트리밍을 위해 청크 전송 인코딩을 사용하여 HTTP 스트리밍 연결을 관리합니다.

### Constructor

```python
from synapse_sdk.utils.network import HTTPStreamManager
import requests

session = requests.Session()
limits = StreamLimits()
manager = HTTPStreamManager(session, limits)
```

### Methods

#### `stream_logs(url, headers, timeout, context)`

청크 전송 인코딩을 사용하여 HTTP 엔드포인트에서 로그를 스트리밍합니다.

```python
# 사용자 정의 timeout으로 로그 스트리밍
for log_line in manager.stream_logs(
    url="http://ray-cluster:8265/logs/stream",
    headers={"Authorization": "Bearer token"},
    timeout=(5, 60),  # (connect, read) timeout
    context="job job-12345"
):
    if 'ERROR' in log_line:
        print(f"오류 감지: {log_line}")
```

### 기능

- **자동 리소스 정리**: HTTP 응답이 적절하게 닫힘
- **라인 크기 필터링**: 대용량 라인 (>10KB)이 자동으로 필터링됨
- **스트림 제한**: 메모리 고갈 방지
- **오류 복구**: 적절한 정리를 통한 강력한 오류 처리

### 오류 처리

- **503**: 연결 거부 또는 네트워크 오류
- **408**: 연결 또는 읽기 timeout
- **404**: 엔드포인트를 찾을 수 없음
- **429**: 스트림 제한 초과
- **500**: 예상치 못한 스트리밍 오류

## 유효성 검사 함수

### `validate_resource_id(resource_id, resource_name='resource')`

주입 공격을 방지하기 위해 리소스 식별자를 유효성 검사합니다.

```python
from synapse_sdk.utils.network import validate_resource_id

# 유효한 사용
job_id = validate_resource_id('job-12345', 'job')
node_id = validate_resource_id('node_abc_123', 'node')

# 잘못된 사용은 ClientError를 발생시킴
try:
    validate_resource_id('job/../malicious', 'job')
except ClientError as e:
    print(f"잘못된 ID: {e}")  # Status 400
```

#### 유효성 검사 규칙

- 비어있으면 안됨
- 영숫자, 하이픈, 밑줄만 허용
- 최대 길이: 100자
- 패턴: `^[a-zA-Z0-9\-_]+$`

#### Parameters

- `resource_id` (Any): 유효성 검사할 ID (문자열로 변환됨)
- `resource_name` (str): 오류 메시지를 위한 이름 (기본값: 'resource')

#### Returns

- `str`: 유효성 검사된 리소스 ID

#### Raises

- `ClientError` (400): 유효성 검사 실패 시

### `validate_timeout(timeout, max_timeout=300)`

경계 확인을 통한 timeout 값 유효성 검사입니다.

```python
from synapse_sdk.utils.network import validate_timeout

# 유효한 timeout
timeout = validate_timeout(30)      # 30초
timeout = validate_timeout(10.5)    # 10.5초

# 잘못된 timeout은 ClientError를 발생시킴
try:
    validate_timeout(-1)     # 음수 timeout
    validate_timeout(500)    # 최대값 초과
except ClientError as e:
    print(f"잘못된 timeout: {e}")  # Status 400
```

#### Parameters

- `timeout` (int|float): 초 단위 timeout 값
- `max_timeout` (int): 허용되는 최대 timeout (기본값: 300)

#### Returns

- `float`: 유효성 검사된 timeout 값

#### Raises

- `ClientError` (400): timeout이 유효하지 않은 경우

## URL Utilities

### `http_to_websocket_url(http_url)`

HTTP URL을 WebSocket URL로 변환합니다.

```python
from synapse_sdk.utils.network import http_to_websocket_url

# URL 변환
ws_url = http_to_websocket_url("http://ray-cluster:8265/logs/")
# 결과: "ws://ray-cluster:8265/logs/"

wss_url = http_to_websocket_url("https://ray-cluster:8265/logs/")
# 결과: "wss://ray-cluster:8265/logs/"
```

#### Parameters

- `http_url` (str): HTTP 또는 HTTPS URL

#### Returns

- `str`: WebSocket URL (ws:// 또는 wss://)

## 오류 Utilities

### `sanitize_error_message(message, context)`

디버깅 컨텍스트를 유지하면서 정보 유출을 방지하기 위해 오류 메시지를 정제합니다.

```python
from synapse_sdk.utils.network import sanitize_error_message

# 로깅을 위한 오류 정제
clean_message = sanitize_error_message(
    "Connection failed: Invalid token abc123",
    "job job-12345"
)
# 결과: 컨텍스트가 포함된 정제된 오류 메시지
```

#### Parameters

- `message` (str): 원본 오류 메시지
- `context` (str): 디버깅을 위한 컨텍스트 (예: "job job-12345")

#### Returns

- `str`: 정제된 오류 메시지

## 완전한 예제

```python
import asyncio
from concurrent.futures import ThreadPoolExecutor
from synapse_sdk.utils.network import (
    StreamLimits,
    WebSocketStreamManager,
    HTTPStreamManager,
    validate_resource_id,
    validate_timeout,
    http_to_websocket_url
)

class StreamingExample:
    def __init__(self):
        # 구성 요소 설정
        self.thread_pool = ThreadPoolExecutor(max_workers=3)
        self.limits = StreamLimits(max_lines=10000)
        self.ws_manager = WebSocketStreamManager(self.thread_pool, self.limits)

        # HTTP 스트리밍을 위한 HTTP 세션
        import requests
        self.session = requests.Session()
        self.http_manager = HTTPStreamManager(self.session, self.limits)

    def stream_job_logs(self, job_id, protocol='websocket'):
        # 입력 유효성 검사
        validated_id = validate_resource_id(job_id, 'job')
        timeout = validate_timeout(30)

        if protocol == 'websocket':
            return self._websocket_stream(validated_id, timeout)
        else:
            return self._http_stream(validated_id, timeout)

    def _websocket_stream(self, job_id, timeout):
        url = f"http://ray-cluster:8265/jobs/{job_id}/logs/"
        ws_url = http_to_websocket_url(url)
        headers = {"Authorization": "Bearer token"}
        context = f"job {job_id}"

        return self.ws_manager.stream_logs(ws_url, headers, timeout, context)

    def _http_stream(self, job_id, timeout):
        url = f"http://ray-cluster:8265/jobs/{job_id}/logs/stream"
        headers = {"Authorization": "Bearer token"}
        timeout_tuple = (5, timeout)
        context = f"job {job_id}"

        return self.http_manager.stream_logs(url, headers, timeout_tuple, context)

# 사용법
example = StreamingExample()

# WebSocket으로 스트리밍
for log_line in example.stream_job_logs('job-12345', 'websocket'):
    print(log_line.strip())

# HTTP 폴백으로 스트리밍
for log_line in example.stream_job_logs('job-12345', 'http'):
    print(log_line.strip())
```

## 모범 사례

### 1. 리소스 관리

```python
# 항상 적절한 정리 사용
thread_pool = ThreadPoolExecutor(max_workers=5)
try:
    manager = WebSocketStreamManager(thread_pool, StreamLimits())
    # 매니저 사용...
finally:
    thread_pool.shutdown(wait=True)
```

### 2. 오류 처리

```python
from synapse_sdk.clients.exceptions import ClientError

try:
    job_id = validate_resource_id(user_input, 'job')
    timeout = validate_timeout(user_timeout)
    # 유효성 검사된 입력으로 진행...
except ClientError as e:
    logger.error(f"유효성 검사 실패: {e}")
    return error_response(e.status, str(e))
```

### 3. 스트림 제한 구성

```python
# 사용 사례에 따라 제한 구성
production_limits = StreamLimits(
    max_messages=20000,      # 프로덕션을 위해 더 높게
    max_lines=100000,        # 더 많은 라인 허용
    max_bytes=200 * 1024 * 1024,  # 큰 로그를 위해 200MB
    queue_size=2000          # 더 큰 버퍼
)
```

## 참고

- [RayClient](../clients/ray.md) - 네트워크 유틸리티의 주요 소비자
- [File Utils](./file.md) - 파일 작업 및 처리
- [Storage](./storage.md) - Storage 제공자