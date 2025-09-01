---
id: faq
title: 자주 묻는 질문
sidebar_position: 9
---

# 자주 묻는 질문

Synapse SDK에 대한 일반적인 질문과 답변입니다.

## 설치 및 설정

### Q: 지원되는 Python 버전은 무엇인가요?

Synapse SDK는 **Python 3.10 이상**이 필요합니다.

```bash
pip install "synapse-sdk[all,devtools]"
```

### Q: 로컬 개발을 위해 code-server를 어떻게 설치하나요?

여러 가지 옵션이 있습니다:

```bash
# 권장: 설치 스크립트
curl -fsSL https://code-server.dev/install.sh | sh

# npm 사용
npm install -g code-server

# yarn 사용
yarn global add code-server
```

더 많은 설치 방법은 다음을 참조하세요: [code-server 설치 가이드](https://coder.com/docs/code-server/latest/install)

## CLI 사용

### Q: Synapse CLI를 어떻게 시작하나요?

간단히 실행하세요:

```bash
synapse
```

이것은 모든 Synapse 기능에 액세스할 수 있는 대화형 메뉴를 엽니다.

### Q: Agent와 로컬 code-server의 차이점은 무엇인가요?

- **Agent Code-Server**: 프로젝트 파일이 동기화된 원격 Agent에서 실행됩니다. 플러그인 암호화 및 보안 전송이 포함됩니다.
- **로컬 Code-Server**: 로컬 머신에서 실행됩니다. 더 빠른 시작, 로컬 환경 및 설정을 사용합니다.

### Q: code-server 포트를 어떻게 설정하나요?

Code-server 포트는 `~/.config/code-server/config.yaml`에서 자동으로 감지됩니다. 설정이 없으면 포트 8070을 기본값으로 사용합니다.

예제 설정:

```yaml
bind-addr: 127.0.0.1:8070
auth: password
password: your-password-here
cert: false
```

### Q: Agent 작업공간 경로가 로컬 경로와 다른 이유는 무엇인가요?

Agent는 로컬 프로젝트가 `/home/coder/workspace`에 마운트되는 컨테이너화된 환경에서 실행됩니다. 이는 정상적이며 다양한 개발 환경에서 일관된 경로를 보장합니다.

## Code-Server 문제 해결

### Q: Code-server에서 "사용 불가능" 오류가 표시됩니다

이는 일반적으로 다음을 의미합니다:

1. Agent에 code-server 지원이 활성화되어 있지 않음
2. 네트워크 연결 문제
3. Agent가 적절히 설정되지 않음

**해결방법**: code-server 지원으로 Agent를 재설치하거나 Agent 설정을 확인하세요.

### Q: 브라우저가 자동으로 열리지 않습니다

이는 헤드리스 환경이나 디스플레이를 사용할 수 없을 때 발생합니다.

**해결방법**: 제공된 URL(`?folder=` 매개변수 포함)을 브라우저에 수동으로 복사하세요.

### Q: 작업공간에서 플러그인이 감지되지 않습니다

**해결방법**: 디렉토리에 플러그인 메타데이터가 포함된 유효한 `config.yaml` 파일이 있는지 확인하세요:

```yaml
name: my-plugin
version: 1.0.0
description: My awesome plugin
entry_point: main.py
```

### Q: 플러그인 암호화는 어떻게 작동하나요?

Agent로 code-server를 열 때 Synapse는:

1. 작업공간에 플러그인이 포함되어 있는지 감지
2. 플러그인 파일의 ZIP 아카이브 생성
3. AES-256 암호화를 사용하여 아카이브 암호화
4. Agent로 안전하게 전송
5. Agent 작업공간에서 암호 해제 및 추출

이렇게 하면 전송 중 플러그인 코드가 보호됩니다.

## 설정

### Q: 설정 파일은 어디에 저장되나요?

- **Synapse 설정**: `~/.synapse/devtools.yaml`
- **Code-Server 설정**: `~/.config/code-server/config.yaml`

### Q: 설정을 어떻게 재설정하나요?

```bash
# 설정 파일 제거
rm ~/.synapse/devtools.yaml
rm ~/.config/code-server/config.yaml

# 설정 마법사 실행
synapse config
```

### Q: "유효하지 않은 토큰 (401)" 오류가 발생하면 어떻게 하나요?

이는 API 토큰이 만료되었거나 유효하지 않음을 의미합니다.

**해결방법**:

1. Synapse 백엔드에서 새 토큰 생성
2. `synapse config`를 실행하여 토큰 업데이트
3. `synapse --dev-tools`로 연결 테스트

## 플러그인 개발

### Q: 새 플러그인을 어떻게 생성하나요?

대화형 플러그인 생성기를 사용하세요:

```bash
synapse
# "🔌 Plugin Management" → "Create new plugin" 선택
```

이것은 예제와 문서가 포함된 완전한 플러그인 구조를 생성합니다.

### Q: 플러그인을 로컬에서 어떻게 테스트하나요?

```bash
# 로컬 스크립트 실행으로 테스트
synapse plugin run my_action '{"param": "value"}' --run-by script

# Agent 실행으로 테스트
synapse plugin run my_action '{"param": "value"}' --run-by agent
```

게시하기 전에 항상 로컬에서 테스트하여 플러그인이 올바르게 작동하는지 확인하세요.

### Q: 플러그인 게시가 오류와 함께 실패합니다

일반적인 문제:

1. **누락된 의존성**: `requirements.txt`에 필요한 모든 패키지가 포함되어 있는지 확인
2. **구문 오류**: 먼저 `--run-by script`로 로컬 테스트
3. **설정 오류**: `config.yaml` 형식과 필수 필드 확인
4. **백엔드 연결**: 백엔드에 액세스할 수 있고 토큰이 유효한지 확인

**해결방법**: 자세한 오류 정보를 위해 디버그 모드를 사용하세요:

```bash
synapse plugin publish --debug
```