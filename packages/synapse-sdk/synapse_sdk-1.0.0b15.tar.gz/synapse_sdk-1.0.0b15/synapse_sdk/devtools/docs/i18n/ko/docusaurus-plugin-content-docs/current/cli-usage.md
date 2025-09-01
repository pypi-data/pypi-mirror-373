---
id: cli-usage
title: CLI 사용 가이드
sidebar_position: 4
---

# CLI 사용 가이드

Synapse SDK는 설정부터 플러그인 개발 및 코드 편집까지 개발 워크플로우를 관리하기 위한 강력한 대화형 CLI를 제공합니다.

## 시작하기

대화형 CLI 실행:

```bash
synapse
```

또는 특정 명령을 직접 실행:

```bash
# 개발 도구 즉시 시작
synapse --dev-tools

# 도움말 표시
synapse --help
```

## 메인 메뉴 옵션

`synapse`를 실행하면 메인 메뉴가 표시됩니다:

```
🚀 Synapse SDK
Select an option:
  🌐 Run Dev Tools
  💻 Open Code-Server IDE
  ⚙️  Configuration
  🔌 Plugin Management
  🚪 Exit
```

## 🌐 Run Dev Tools

다음 기능을 포함한 Synapse 개발 도구 대시보드를 실행합니다:

- **대화형 UI**: Agent와 작업 관리를 위한 웹 기반 대시보드
- **실시간 모니터링**: Agent 상태 및 작업 실행의 실시간 보기
- **플러그인 관리**: UI를 통한 플러그인 업로드, 테스트, 관리

### 사용법
```bash
# CLI 메뉴에서 개발 도구 실행
synapse

# 또는 직접 시작
synapse --dev-tools
```

## 💻 Open Code-Server IDE

플러그인 개발을 위한 웹 기반 VS Code 환경을 엽니다. Agent 기반 및 로컬 code-server 인스턴스를 모두 지원합니다.

### Agent Code-Server

Agent에서 실행되는 원격 code-server에 연결:

- **자동 설정**: Synapse가 작업공간을 설정하고 의존성을 설치
- **플러그인 암호화**: 로컬 플러그인 코드가 암호화되어 안전하게 전송
- **작업공간 동기화**: 로컬 프로젝트가 Agent 환경에서 사용 가능

### 로컬 Code-Server

로컬 code-server 인스턴스 실행:

- **포트 감지**: `~/.config/code-server/config.yaml`에서 포트를 자동으로 읽음
- **폴더 매개변수**: 올바른 작업공간 디렉토리로 열림
- **브라우저 통합**: 적절한 URL로 자동으로 브라우저를 열음

### 사용 예제

```bash
# 대화형 메뉴 (권장)
synapse
# "💻 Open Code-Server IDE" 선택

# 직접 명령
synapse code-server

# 특정 옵션과 함께
synapse code-server --agent my-agent --workspace /path/to/project

# 브라우저를 자동으로 열지 않음
synapse code-server --no-open-browser
```

### Code-Server 옵션

| 옵션 | 설명 | 기본값 |
|--------|-------------|---------|
| `--agent` | 사용할 특정 Agent ID | 현재 Agent 또는 프롬프트 |
| `--workspace` | 프로젝트 디렉토리 경로 | 현재 디렉토리 |
| `--open-browser/--no-open-browser` | 브라우저 자동 열기 | `--open-browser` |

### 로컬 Code-Server 설치

code-server가 로컬에 설치되지 않은 경우 CLI가 설치 지침을 제공합니다:

```bash
# 권장: 설치 스크립트
curl -fsSL https://code-server.dev/install.sh | sh

# npm 사용
npm install -g code-server

# yarn 사용
yarn global add code-server
```

더 많은 옵션은 다음을 참조하세요: https://coder.com/docs/code-server/latest/install

## ⚙️ Configuration

다음을 설정하기 위한 대화형 설정 마법사:

- **백엔드 연결**: API 엔드포인트 및 인증 설정
- **Agent 선택**: 개발 Agent 선택 및 설정
- **토큰 관리**: 액세스 토큰 및 인증 관리

### 설정 파일

Synapse는 다음 위치에 설정을 저장합니다:
- **백엔드 설정**: `~/.synapse/devtools.yaml`
- **Agent 설정**: `~/.synapse/devtools.yaml` (Agent 섹션)
- **Code-Server 설정**: `~/.config/code-server/config.yaml`

## 🔌 Plugin Management

포괄적인 플러그인 개발 및 관리 도구:

### 새 플러그인 생성

```bash
synapse
# "🔌 Plugin Management" → "Create new plugin" 선택
```

대화형 마법사가 다음을 생성합니다:
- 플러그인 디렉토리 구조
- 설정 파일 (`config.yaml`)
- 예제 플러그인 코드
- 요구사항 및 의존성

### 플러그인 로컬 실행

다른 환경에서 플러그인 테스트:

```bash
# 스크립트 실행 (로컬)
synapse plugin run my_action '{"param": "value"}' --run-by script

# Agent 실행 (원격)
synapse plugin run my_action '{"param": "value"}' --run-by agent

# 백엔드 실행 (클라우드)
synapse plugin run my_action '{"param": "value"}' --run-by backend
```

### 플러그인 게시

Synapse 백엔드에 플러그인 배포:

```bash
synapse
# "🔌 Plugin Management" → "Publish plugin" 선택
```

옵션:
- **디버그 모드**: 자세한 로깅으로 배포 테스트
- **프로덕션 모드**: 실제 사용을 위한 배포

## 명령 참조

### 주요 명령어

```bash
# 대화형 CLI (메인 메뉴)
synapse

# 개발 도구
synapse --dev-tools

# 직접 명령
synapse config         # 설정 마법사
synapse devtools       # 개발 대시보드
synapse code-server    # 코드 편집 환경
synapse plugin         # 플러그인 관리
```

### Code-Server 명령

```bash
synapse code-server [OPTIONS]

Options:
  --agent TEXT                    Agent 이름 또는 ID
  --open-browser / --no-open-browser
                                  브라우저에서 열기 [기본값: open-browser]
  --workspace TEXT                작업공간 디렉토리 경로 (기본값: 현재 디렉토리)
  --help                          이 메시지를 표시하고 종료.
```

### 플러그인 명령어

```bash
# 플러그인 생성
synapse plugin create

# 플러그인 실행
synapse plugin run ACTION PARAMS [OPTIONS]

# 플러그인 게시
synapse plugin publish [OPTIONS]
```

## 팁 및 모범 사례

### Code-Server 개발

1. **플러그인 감지**: code-server를 열 때 Synapse는 작업공간에 플러그인이 포함되어 있는지 자동으로 감지하고 Agent로의 안전한 전송을 위해 암호화합니다.

2. **작업공간 경로**: Agent 작업공간은 일반적으로 `/home/coder/workspace`를 사용합니다 - 이는 컨테이너화된 환경에서 정상입니다.

3. **포트 설정**: 로컬 code-server 포트는 설정 파일에서 읽어오며, 설정이 없으면 8070을 기본값으로 사용합니다.

### 설정 관리

1. **토큰 보안**: API 토큰을 안전하게 저장하고 정기적으로 순환
2. **Agent 선택**: Agent의 목적을 식별하기 위해 설명적인 Agent 이름 사용
3. **백엔드 URL**: 백엔드 URL이 개발 환경에서 접근 가능한지 확인

### 플러그인 개발

1. **로컬 테스트**: 배포 전에 항상 `--run-by script`로 플러그인을 로컬에서 테스트
2. **디버그 모드**: 초기 배포 시 디버그 모드를 사용하여 문제를 조기에 발견
3. **버전 제어**: git을 사용하여 플러그인 변경사항을 추적하고 버전 관리

## 문제 해결

### Code-Server 문제

**문제**: "Code-server is not available" 오류
- **해결방법**: Agent에 code-server 지원이 활성화되어 있는지 확인

**문제**: 브라우저가 자동으로 열리지 않음
- **해결방법**: 제공된 URL을 브라우저에 수동으로 복사

**문제**: 잘못된 포트가 표시됨
- **해결방법**: 올바른 포트 설정을 위해 `~/.config/code-server/config.yaml` 확인

### 설정 문제

**문제**: "No backend configured"
- **해결방법**: `synapse config`를 실행하여 백엔드 연결 설정

**문제**: "Invalid token (401)"
- **해결방법**: 새 API 토큰을 생성하고 설정 업데이트

**문제**: "Connection timeout"
- **해결방법**: 네트워크 연결 및 백엔드 URL 접근성 확인

### 플러그인 문제

**문제**: 작업공간에서 플러그인이 감지되지 않음
- **해결방법**: 디렉토리에 유효한 `config.yaml` 파일이 있는지 확인

**문제**: 플러그인 실행 실패
- **해결방법**: 플러그인 의존성 및 구문 확인, 먼저 로컬에서 테스트

더 많은 문제 해결 도움은 [문제 해결 가이드](./troubleshooting.md)를 참조하세요.