---
id: contributing
title: 기여하기
sidebar_position: 12
---

# Synapse SDK에 기여하기

Synapse SDK에 기여해 주셔서 감사합니다! 이 가이드는 프로젝트 기여를 시작하는 데 도움이 됩니다.

## 개발 환경 설정

### 사전 요구사항

- Python 3.8 이상
- Git
- 가상 환경 도구 (venv, conda 등)

### 시작하기

1. **저장소 포크 및 복제**
   ```bash
   git clone https://github.com/yourusername/synapse-sdk.git
   cd synapse-sdk
   ```

2. **가상 환경 생성**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   ```

3. **의존성 설치**
   ```bash
   pip install -r requirements.txt
   pip install -r requirements.test.txt
   ```

## 코드 포맷팅 및 품질

### Ruff 포맷팅

코드 포맷팅 및 린팅에 **Ruff**를 사용합니다. 모든 기여는 우리의 포맷팅 표준을 따라야 합니다.

#### 필수 명령어

코드 변경 사항을 제출하기 전에 다음 명령어를 실행하세요:

```bash
# 모든 Python 코드 포맷팅
ruff format .

# 린팅 문제 수정
ruff check --fix .

# 남은 문제 확인
ruff check .
```

#### 포맷팅 워크플로우

1. **변경사항 작성** - Python 코드를 작성하거나 수정
2. **Ruff로 포맷팅** - `ruff format .`을 실행하여 일관된 포맷팅 적용
3. **린팅 문제 수정** - `ruff check --fix .`를 실행하여 코드 품질 문제 해결
4. **변경사항 확인** - 포맷팅된 코드를 검토하여 정확성 보장
5. **변경사항 커밋** - 적절히 포맷팅된 코드로 커밋 생성

#### IDE 통합

IDE가 Ruff를 자동으로 실행하도록 설정하세요:

- **VS Code**: Ruff 확장 프로그램 설치
- **PyCharm**: Ruff를 외부 도구로 설정
- **Vim/Neovim**: ruff-lsp 또는 유사한 플러그인 사용

### 코드 스타일 가이드라인

- **줄 길이**: `pyproject.toml`의 프로젝트별 설정 따르기
- **Import 정렬**: Ruff가 import 정리를 처리하도록 함
- **타입 힌트**: 적절한 곳에 타입 어노테이션 사용
- **독스트링**: Google 스타일 독스트링 형식 따르기
- **주석**: 복잡한 로직에 대해 명확하고 간결한 주석 작성

## 테스팅

### 테스트 실행

```bash
# 모든 테스트 실행
pytest

# 특정 테스트 파일 실행
pytest tests/plugins/utils/test_config.py

# 커버리지와 함께 실행
pytest --cov=synapse_sdk
```

### 테스트 작성

- 모든 새로운 기능에 대해 테스트 작성
- 시나리오를 설명하는 서술적 테스트 이름 사용
- 긍정적 및 부정적 테스트 케이스 모두 포함
- 외부 의존성을 적절히 모킹
- 높은 테스트 커버리지 유지

#### 테스트 구조

```python
class TestMyFeature:
    """MyFeature 기능 테스트."""
    
    def test_feature_success_case(self):
        """성공적인 기능 작동 테스트."""
        # Arrange
        input_data = {"key": "value"}
        
        # Act
        result = my_feature(input_data)
        
        # Assert
        assert result == expected_output
    
    def test_feature_error_case(self):
        """기능 오류 처리 테스트."""
        with pytest.raises(ValueError, match="Expected error message"):
            my_feature(invalid_input)
```

## 플러그인 개발

### 새로운 플러그인 유틸리티 생성

새로운 플러그인 유틸리티를 추가할 때:

1. **적절한 모듈에 추가**:
   - 설정 유틸리티 → `synapse_sdk/plugins/utils/config.py`
   - 액션 유틸리티 → `synapse_sdk/plugins/utils/actions.py`
   - 레지스트리 유틸리티 → `synapse_sdk/plugins/utils/registry.py`

2. **포괄적인 독스트링 포함**:
   ```python
   def my_utility_function(param: str) -> Dict[str, Any]:
       """함수에 대한 간단한 설명.
       
       Args:
           param: 매개변수 설명.
           
       Returns:
           반환값 설명.
           
       Raises:
           ValueError: 입력이 유효하지 않을 때.
           
       Examples:
           >>> my_utility_function("example")
           {'result': 'processed'}
       """
   ```

3. **`__all__` 내보내기에 추가**
4. **포괄적인 테스트 작성**
5. **문서 업데이트**

### 플러그인 카테고리

플러그인 카테고리 작업 시:

- 가능하면 기존 카테고리 사용
- 명명 규칙 따르기: `snake_case`
- 적절한 검증 및 오류 처리 추가
- 새 카테고리 추가 시 카테고리 enum 업데이트

## 문서화

### API 문서화

- 모든 공개 함수에 대한 독스트링 업데이트
- 독스트링에 사용 예제 포함
- 더 나은 IDE 지원을 위한 타입 힌트 추가
- 오류 조건 및 예외 문서화

### 사용자 문서화

관련 문서 파일 업데이트:

- **API 참조**: `docs/api/plugins/utils.md`
- **기능 가이드**: `docs/features/plugins/index.md`
- **변경 로그**: `docs/changelog.md`
- **예제**: 실용적인 사용 예제 추가

### 문서화 형식

다음을 포함한 명확하고 간결한 언어 사용:

- 모든 함수에 대한 코드 예제
- 매개변수 및 반환값 설명
- 오류 처리 예제
- 호환성을 깨뜨리는 변경에 대한 마이그레이션 가이드

## Pull Request 프로세스

### 제출 전

1. **포맷팅 및 린팅 실행**:
   ```bash
   ruff format .
   ruff check --fix .
   ```

2. **모든 테스트 실행**:
   ```bash
   pytest
   ```

3. **필요에 따라 문서 업데이트**

4. **중요한 변경사항에 대한 변경 로그 항목 추가**

### Pull Request 가이드라인

- **명확한 제목**: PR이 달성하는 것 설명
- **자세한 설명**: 변경사항과 동기 설명
- **이슈 참조**: 관련 GitHub 이슈에 링크
- **테스트 커버리지**: 새 코드가 테스트되었는지 확인
- **문서화**: 사용자 대상 변경사항에 대한 문서 업데이트

### PR 템플릿

```markdown
## 설명
변경사항에 대한 간단한 설명

## 변경 유형
- [ ] 버그 수정
- [ ] 새로운 기능
- [ ] 호환성을 깨뜨리는 변경
- [ ] 문서 업데이트

## 테스트
- [ ] 로컬에서 테스트 통과
- [ ] 새 기능에 대한 새 테스트 추가
- [ ] Ruff로 코드 포맷팅됨

## 문서화
- [ ] API 문서 업데이트됨
- [ ] 필요시 사용자 가이드 업데이트됨
- [ ] 변경 로그 항목 추가됨
```

## 코드 리뷰

### 리뷰 기준

- **기능성**: 코드가 의도된 대로 작동
- **품질**: 코딩 표준 및 모범 사례 준수
- **테스팅**: 적절한 테스트 커버리지
- **문서화**: 공개 API에 대한 명확한 문서
- **성능**: 명백한 성능 문제 없음
- **보안**: 보안 취약점 없음

### 피드백 대응

- 모든 리뷰어 의견 처리
- 피드백이 불명확하면 설명 요청
- 요청된 변경사항을 신속히 수행
- 변경 후 포맷팅 및 테스트 재실행

## 프로젝트 구조

프로젝트 조직 이해:

```
synapse_sdk/
├── plugins/
│   ├── utils/              # 플러그인 유틸리티 (모듈식)
│   │   ├── config.py       # 설정 유틸리티
│   │   ├── actions.py      # 액션 관리
│   │   └── registry.py     # 레지스트리 유틸리티
│   ├── categories/         # 플러그인 카테고리 구현
│   └── models.py          # 핵심 플러그인 모델
├── clients/               # API 클라이언트
├── utils/                 # 일반 유틸리티
└── devtools/             # 개발 도구

tests/
├── plugins/
│   └── utils/            # 플러그인 유틸리티 테스트
└── ...                   # 기타 테스트 모듈

docs/                     # 문서
├── api/                  # API 참조
├── features/             # 기능 가이드
└── changelog.md          # 변경 로그
```

## 도움 받기

- **GitHub Issues**: 버그 신고 또는 기능 요청
- **Discussions**: 질문하거나 아이디어 논의
- **문서화**: 먼저 기존 문서 확인
- **코드 리뷰**: 리뷰 중 설명 요청

## 라이센스

Synapse SDK에 기여함으로써 귀하의 기여가 프로젝트와 동일한 라이센스(MIT 라이센스) 하에 라이센스될 것에 동의합니다.