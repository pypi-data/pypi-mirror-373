---
id: quickstart
title: 빠른 시작 가이드
sidebar_position: 3
---

# 빠른 시작 가이드

Synapse SDK를 몇 분 안에 시작하고 실행하세요.

## 대화형 CLI

모든 기능에 대화형 메뉴를 통해 접근하기 위해 Synapse CLI를 실행하세요:

```bash
synapse
```

다음 옵션들이 있는 메인 메뉴가 열립니다:

- 🌐 **개발 도구**: 에이전트 및 작업 관리를 위한 웹 기반 대시보드
- 💻 **Code-Server IDE**: 플러그인 개발을 위한 웹 기반 VS Code
- ⚙️ **설정**: 백엔드 연결 및 에이전트 설정
- 🔌 **플러그인 관리**: 플러그인 생성, 테스트 및 게시

## 빠른 명령어

특정 기능에 빠르게 접근하기 위해:

```bash
# 개발 도구 즉시 시작
synapse --dev-tools

# 백엔드 및 에이전트 구성
synapse config

# 코드 편집 환경 열기
synapse code-server

# 새 플러그인 생성
synapse plugin create
```

## 첫 번째 플러그인

1. **플러그인 생성**:

   ```bash
   synapse
   # "🔌 플러그인 관리" → "새 플러그인 생성" 선택
   ```

2. **Code-Server에서 편집**:

   ```bash
   synapse
   # "💻 Code-Server IDE 열기" 선택
   ```

3. **로컬에서 테스트**:

   ```bash
   synapse plugin run my_action '{"param": "value"}' --run-by script
   ```

4. **백엔드에 게시**:

   ```bash
   synapse
   # "🔌 플러그인 관리" → "플러그인 게시" 선택
   ```

## 다음 단계

- 완전한 [CLI 사용 가이드](./cli-usage.md) 읽기
- [핵심 개념](./concepts/index.md)에 대해 학습하기
- [API 참조](./api/index.md) 탐색하기
- [자주 묻는 질문](./faq.md) 확인하기