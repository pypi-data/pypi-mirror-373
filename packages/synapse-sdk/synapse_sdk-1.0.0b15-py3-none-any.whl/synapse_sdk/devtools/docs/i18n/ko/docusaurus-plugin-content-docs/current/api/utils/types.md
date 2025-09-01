---
id: types
title: Custom Types
sidebar_position: 3
---

# Custom Types

SDK 전반에 걸쳐 사용되는 사용자 정의 타입 및 Pydantic 필드입니다.

## FileField

자동 다운로드 기능이 있는 파일 URL 처리를 위한 사용자 정의 Pydantic 필드입니다.

```python
from synapse_sdk.types import FileField
from pydantic import BaseModel

class MyParams(BaseModel):
    input_file: FileField  # 파일을 자동으로 다운로드

def process(params: MyParams):
    file_path = params.input_file  # 로컬 파일 경로
    # 파일 처리...
```

### 기능

- URL에서 자동 파일 다운로드
- 임시 파일 관리
- 다양한 파일 형식 지원
- 파일 존재 여부 유효성 검사

## 사용 예제

```python
# 플러그인 매개변수에서
class ProcessParams(BaseModel):
    data_file: FileField
    config_file: FileField = None  # 선택적 파일

# FileField는 자동으로:
# 1. URL에서 파일 다운로드
# 2. 파일 존재 여부 유효성 검사
# 3. 로컬 파일 경로 반환
# 4. 임시 파일 정리
```

## 타입 유효성 검사

SDK 전반에 걸쳐 타입 안전성을 보장하기 위한 사용자 정의 유효성 검사기입니다.