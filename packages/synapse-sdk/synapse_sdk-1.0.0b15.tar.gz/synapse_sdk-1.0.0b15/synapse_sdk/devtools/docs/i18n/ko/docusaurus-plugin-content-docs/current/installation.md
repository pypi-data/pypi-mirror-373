---
id: installation
title: 설치 & 설정
sidebar_position: 2
---

# 설치 & 설정

Synapse SDK를 몇 분 안에 시작해보세요.

## 사전 요구사항

Synapse SDK를 설치하기 전에 다음을 확인하세요:

- **Python 3.10 이상** 설치됨

## 설치 방법

### PyPI에서 설치

Synapse SDK를 설치하는 가장 쉬운 방법은 pip를 사용하는 것입니다:

```bash
pip install synapse-sdk
```

### 선택적 종속성과 함께 설치

추가 기능을 위해 extras와 함께 설치하세요:

```bash
# 모든 종속성과 함께 설치 (분산 컴퓨팅, 최적화 라이브러리)
pip install synapse-sdk[all]

# 대시보드 종속성과 함께 설치 (FastAPI, Uvicorn)
pip install synapse-sdk[devtools]

# 둘 다 설치
pip install "synapse-sdk[all,devtools]"
```

### 소스에서 설치

최신 개발 버전을 가져오려면:

```bash
git clone https://github.com/datamaker/synapse-sdk.git
cd synapse-sdk
pip install -e .

# 선택적 종속성과 함께
pip install -e ".[all,devtools]"
```

## 설치 확인

설치 후 모든 것이 작동하는지 확인하세요:

```bash
# 버전 확인
synapse --version

# 대화형 CLI 실행
synapse

# devtools와 함께 실행
synapse --dev-tools
```

## 문제 해결

### 일반적인 문제들

1. **ImportError: No module named 'synapse_sdk'**
   - 가상 환경을 활성화했는지 확인하세요
   - Python 경로 확인: `python -c "import sys; print(sys.path)"`

2. **백엔드 연결 시간 초과**
   - API 토큰이 올바른지 확인하세요
   - 네트워크 연결을 확인하세요
   - 백엔드 URL에 접근 가능한지 확인하세요

### 도움 받기

문제가 발생하면:

1. [문제 해결 가이드](./troubleshooting.md)를 확인하세요
2. [GitHub Issues](https://github.com/datamaker/synapse-sdk/issues) 검색
3. [Discord 커뮤니티](https://discord.gg/synapse-sdk)에 참여하세요

## 다음 단계

- [빠른 시작 가이드](./quickstart.md) 따라하기
- [핵심 개념](./concepts/index.md)에 대해 학습하기