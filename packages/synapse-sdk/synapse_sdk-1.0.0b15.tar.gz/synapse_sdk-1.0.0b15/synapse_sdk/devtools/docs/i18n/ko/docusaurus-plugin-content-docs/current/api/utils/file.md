---
id: file
title: 파일 유틸리티
sidebar_position: 1
---

# 파일 유틸리티

파일 작업 및 처리 유틸리티입니다.

## 파일 작업

### 아카이브 함수

플러그인 아카이브를 생성하고 추출하는 함수입니다.

### 다운로드 함수

URL에서 파일을 다운로드하는 유틸리티입니다.

```python
from synapse_sdk.utils.file import download_file

local_path = download_file(url, destination)
```

### 업로드 함수

청크 업로드 지원을 포함한 파일 업로드 유틸리티입니다.

## 청크 파일 작업

### read_file_in_chunks

효율적인 메모리 사용을 위해 파일을 청크 단위로 읽습니다. 대용량 파일이나 업로드 또는 해싱을 위해 파일을 청크 단위로 처리할 때 특히 유용합니다.

```python
from synapse_sdk.utils.file import read_file_in_chunks

# 기본 50MB 청크로 파일 읽기
for chunk in read_file_in_chunks('/path/to/large_file.bin'):
    process_chunk(chunk)

# 사용자 정의 청크 크기로 읽기 (10MB)
for chunk in read_file_in_chunks('/path/to/file.bin', chunk_size=1024*1024*10):
    upload_chunk(chunk)
```

**매개변수:**

- `file_path` (str | Path): 읽을 파일의 경로
- `chunk_size` (int, 선택사항): 각 청크의 바이트 크기. 기본값은 50MB (52,428,800바이트)

**반환값:**

- 파일 내용 청크를 바이트로 생성하는 제너레이터

**예외:**

- `FileNotFoundError`: 파일이 존재하지 않는 경우
- `PermissionError`: 권한으로 인해 파일을 읽을 수 없는 경우
- `OSError`: 파일 읽기 시 OS 수준 오류가 발생한 경우

### 사용 사례

**대용량 파일 처리**: 메모리에 맞지 않는 대용량 파일을 효율적으로 처리합니다:

```python
import hashlib

def calculate_hash_for_large_file(file_path):
    hash_md5 = hashlib.md5()
    for chunk in read_file_in_chunks(file_path):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()
```

**청크 업로드 통합**: 이 함수는 `CoreClientMixin.create_chunked_upload` 메서드와 완벽하게 통합됩니다:

```python
from synapse_sdk.clients.backend.core import CoreClientMixin

client = CoreClientMixin(base_url='https://api.example.com')
result = client.create_chunked_upload('/path/to/large_file.zip')
```

**모범 사례:**

- 최적의 업로드 성능을 위해 기본 청크 크기(50MB) 사용
- 사용 가능한 메모리와 네트워크 조건에 따라 청크 크기 조정
- 매우 큰 파일(>1GB)의 경우, 더 나은 진행 상황 추적을 위해 작은 청크 사용 고려
- 파일 작업 시 항상 예외 처리

## 체크섬 함수

### get_checksum_from_file

Django 의존성 없이 파일 형태 객체의 체크섬을 계산합니다. 이 함수는 `read()` 메서드가 있는 모든 파일 형태 객체와 함께 작동하며, Django의 File 객체, BytesIO, StringIO, 일반 파일 객체와 호환됩니다.

```python
import hashlib
from io import BytesIO
from synapse_sdk.utils.file import get_checksum_from_file

# BytesIO와 기본 사용법 (기본값은 SHA1)
data = BytesIO(b'Hello, world!')
checksum = get_checksum_from_file(data)
print(checksum)  # 16진수 문자열로 된 SHA1 해시

# 다른 해시 알고리즘 사용
checksum_md5 = get_checksum_from_file(data, digest_mod=hashlib.md5)
checksum_sha256 = get_checksum_from_file(data, digest_mod=hashlib.sha256)

# 실제 파일 객체와 함께 사용
with open('/path/to/file.txt', 'rb') as f:
    checksum = get_checksum_from_file(f)

# StringIO와 함께 사용 (텍스트 파일)
from io import StringIO
text_data = StringIO('Hello, world!')
checksum = get_checksum_from_file(text_data)  # 자동으로 UTF-8로 인코딩
```

**매개변수:**

- `file` (IO[Any]): 청크 단위로 읽기를 지원하는 read() 메서드가 있는 파일 형태 객체
- `digest_mod` (Callable[[], Any], 선택사항): hashlib의 해시 알고리즘. 기본값은 `hashlib.sha1`

**반환값:**

- `str`: 파일 내용의 16진수 다이제스트

**주요 기능:**

- **메모리 효율적**: 대용량 파일을 처리하기 위해 4KB 청크로 파일 읽기
- **자동 파일 포인터 리셋**: 파일 객체가 시킹을 지원하는 경우 시작 위치로 리셋
- **텍스트/바이너리 무관**: 텍스트(StringIO)와 바이너리(BytesIO) 파일 객체 모두 처리
- **Django 의존성 없음**: Django File 객체와 호환되면서도 Django 없이 작동
- **유연한 해시 알고리즘**: 모든 hashlib 알고리즘 지원 (SHA1, SHA256, MD5 등)

**사용 사례:**

**Django 파일 객체 호환성**: Django를 요구하지 않으면서도 Django의 File 객체와 함께 작동합니다:

```python
# Django File 형태 동작 시뮬레이션
class FileWrapper:
    def __init__(self, data):
        self._data = data
        self._pos = 0

    def read(self, size=None):
        if size is None:
            result = self._data[self._pos:]
            self._pos = len(self._data)
        else:
            result = self._data[self._pos:self._pos + size]
            self._pos += len(result)
        return result

file_obj = FileWrapper(b'File content')
checksum = get_checksum_from_file(file_obj)
```

**대용량 파일 처리**: 대용량 파일의 체크섬을 효율적으로 계산합니다:

```python
# 메모리 효율성을 갖춘 대용량 파일 처리
with open('/path/to/large_file.bin', 'rb') as large_file:
    checksum = get_checksum_from_file(large_file, digest_mod=hashlib.sha256)
```

**다중 해시 알고리즘**: 같은 파일에 대해 다른 체크섬을 계산합니다:

```python
algorithms = [
    ('MD5', hashlib.md5),
    ('SHA1', hashlib.sha1),
    ('SHA256', hashlib.sha256),
]

with open('/path/to/file.bin', 'rb') as f:
    checksums = {}
    for name, algo in algorithms:
        f.seek(0)  # 파일 포인터 리셋
        checksums[name] = get_checksum_from_file(f, digest_mod=algo)
```

## 경로 유틸리티

경로 조작 및 검증을 위한 함수입니다.

## 임시 파일

임시 파일 관리 및 정리를 위한 유틸리티입니다.
