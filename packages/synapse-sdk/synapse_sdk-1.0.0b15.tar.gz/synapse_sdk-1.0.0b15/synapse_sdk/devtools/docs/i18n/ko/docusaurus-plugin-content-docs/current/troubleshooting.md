---
id: troubleshooting
title: 문제 해결
sidebar_position: 10
---

# 문제 해결

Synapse SDK 사용 시 발생하는 일반적인 문제와 해결방법입니다.

## 설치 문제

## 인증 문제

### ClientError: 401 Unauthorized

**증상**: API 호출이 401 오류로 실패합니다.

**진단 단계**:


3. **CLI를 통한 토큰 확인**:
   ```bash
   # 토큰을 확인하기 위한 대화형 설정 사용
   synapse config
   # "Show current configuration" 선택
   # 토큰이 검증을 위해 평문으로 표시됩니다
   ```

4. **코드에서 토큰 확인**:
   ```python
   from synapse_sdk.clients.backend import BackendClient
   
   client = BackendClient(
       base_url="https://api.synapse.sh",
       api_token="your-token"  # "Token " 접두사 없음
   )
   
   try:
       user = client.get_current_user()
       print(f"Authenticated as: {user.email}")
   except Exception as e:
       print(f"Auth failed: {e}")
   ```

**일반적인 해결방법**:
- 웹 인터페이스에서 토큰 재생성
- 토큰이 만료되지 않았는지 확인
- 올바른 백엔드 URL 확인

### Agent 인증 오류

**증상**: Agent 관련 작업이 실패합니다.

**해결방법**:

1. **Agent 설정 확인**:
   ```bash
   synapse config
   # "Show current configuration" 선택
   # 백엔드와 Agent 토큰 모두 평문으로 표시됩니다
   ```

2. **Agent 토큰 확인**:
   ```python
   from synapse_sdk.clients.agent import AgentClient
   
   client = AgentClient(
       base_url="https://api.synapse.sh",
       agent_token="your-agent-token"
   )
   ```

## 연결 문제

### 연결 시간 초과

**증상**: 요청이 시간 초과되거나 멈춤 상태가 됩니다.

**해결방법**:

1. **시간 초과 값 증가**:
   ```python
   client = BackendClient(
       base_url="https://api.synapse.sh",
       api_token="your-token",
       timeout={'connect': 30, 'read': 120}
   )
   ```

2. **네트워크 연결 확인**:
   ```bash
   # 기본 연결 테스트
   ping api.synapse.sh
   
   # HTTPS 접근 테스트
   curl -I https://api.synapse.sh/health
   ```

3. **필요시 프록시 설정**:
   ```bash
   export HTTP_PROXY="http://proxy.company.com:8080"
   export HTTPS_PROXY="https://proxy.company.com:8080"
   ```

### DNS 해결 문제

**증상**: "Name or service not known" 오류가 발생합니다.

**해결방법**:

1. **DNS 설정 확인**:
   ```bash
   nslookup api.synapse.sh
   ```

2. **대체 DNS 시도**:
   ```bash
   # Google DNS 임시 사용
   export SYNAPSE_BACKEND_HOST="$(dig @8.8.8.8 api.synapse.sh +short)"
   ```

3. **IP 주소 직접 사용** (임시):
   ```python
   client = BackendClient(base_url="https://192.168.1.100:8000")
   ```

## 플러그인 개발 문제

### 플러그인 가져오기 오류

**증상**: 플러그인 로딩 또는 가져오기가 실패합니다.

**진단**:
```bash
# 플러그인 구문 테스트
python -m py_compile plugin/__init__.py

# 순환 가져오기 확인
python -c "import plugin; print('OK')"
```

**해결방법**:

1. **구문 오류 수정**:
   ```bash
   # 린팅 사용
   pip install ruff
   ruff check plugin/
   ```

2. **가져오기 경로 확인**:
   ```python
   # plugin/__init__.py에서
   from synapse_sdk.plugins.categories.base import Action, register_action
   # 아님: from synapse_sdk.plugins.base import Action
   ```

3. **플러그인 구조 확인**:
   ```
   my-plugin/
   ├── config.yaml
   ├── plugin/
   │   └── __init__.py
   ├── requirements.txt
   └── README.md
   ```

### 플러그인 실행 실패

**증상**: 플러그인이 시작되지만 실행 중 실패합니다.

**디버깅 단계**:

1. **CLI를 통한 디버그 모드 활성화**:
   ```bash
   synapse
   # "Plugin Management" 선택
   # "Run plugin locally" 선택
   # 액션과 매개변수 입력
   # 로컬 실행 시 디버그 모드가 기본적으로 활성화됩니다
   ```

2. **수동으로 디버그 모드 활성화**:
   ```bash
   export SYNAPSE_DEBUG=true
   synapse plugin run --path ./my-plugin --action test
   ```

2. **로그 확인**:
   ```python
   def start(self):
       try:
           self.run.log("Starting plugin execution")
           # 여기에 코드 작성
           self.run.log("Plugin completed successfully")
       except Exception as e:
           self.run.log(f"Error: {str(e)}", level="ERROR")
           raise
   ```

3. **매개변수 검증**:
   ```python
   from pydantic import ValidationError
   
   def start(self):
       try:
           # 매개변수 검증
           params = self.params_model(**self.params)
       except ValidationError as e:
           self.run.log(f"Parameter validation failed: {e}")
           raise
   ```

### 파일 처리 문제

**증상**: 플러그인에서 파일 작업이 실패합니다.

**일반적인 문제 & 해결방법**:

1. **FileField가 다운로드되지 않음**:
   ```python
   # 파일 URL 형식 확인
   class MyParams(BaseModel):
       input_file: FileField  # URL 형식 예상
   
   def start(self):
       file_path = self.params.input_file
       if not os.path.exists(file_path):
           raise FileNotFoundError(f"File not found: {file_path}")
   ```

2. **권한 오류**:
   ```python
   import tempfile
   import shutil
   
   def start(self):
       # 임시 디렉토리 사용
       with tempfile.TemporaryDirectory() as temp_dir:
           output_path = os.path.join(temp_dir, "result.csv")
           # output_path에서 처리 및 저장
   ```

3. **대용량 파일 처리**:
   ```python
   def start(self):
       # 대용량 파일을 청크 단위로 처리
       chunk_size = 1024 * 1024  # 1MB 청크
       with open(self.params.input_file, 'rb') as f:
           while True:
               chunk = f.read(chunk_size)
               if not chunk:
                   break
               process_chunk(chunk)
   ```

## 분산 컴퓨팅 문제

### 클러스터 연결

**증상**: 컴퓨팅 클러스터에 연결할 수 없습니다.

**해결방법**:

1. **클러스터 상태 확인**:
   ```bash
   synapse cluster status
   # 클러스터 정보가 표시되어야 함
   ```

2. **로컬 클러스터 시작**:
   ```bash
   synapse cluster start --dashboard-host=0.0.0.0
   ```

3. **원격 클러스터 연결**:
   ```bash
   export SYNAPSE_CLUSTER_ADDRESS="cluster://remote-cluster:10001"
   synapse cluster status  # 원격 클러스터에 연결되어야 함
   ```

### 메모리 문제

**증상**: 실행 중 메모리 부족 오류가 발생합니다.

**해결방법**:

1. **메모리 할당 증가**:
   ```bash
   synapse cluster start --memory=2000000000  # 2GB
   ```

2. **코드에서 설정**:
   ```python
   from synapse_sdk.compute import init
   init(memory=2000000000)
   ```

3. **데이터를 작은 청크로 처리**:
   ```python
   def process_chunk(data_chunk):
       return process(data_chunk)
   
   # 대용량 데이터를 청크로 분할
   chunks = split_data(large_data)
   results = [process_chunk(chunk) for chunk in chunks]
   ```

### 작업 실패

**증상**: 작업이 시작되지 않거나 완료되지 않습니다.

**해결방법**:

1. **리소스 요구사항 확인**:
   ```python
   def my_task(resources={'cpus': 2, 'memory': '1GB'}):
       pass
   ```

2. **런타임 환경 확인**:
   ```yaml
   # 플러그인 config.yaml에서
   runtime_env:
     pip:
       packages: ["pandas", "numpy"]
   ```

## 개발 도구 문제

### 개발 도구가 시작되지 않음

**증상**: `synapse --dev-tools` 시작이 실패합니다.

**해결방법**:

1. **대시보드 의존성 설치**:
   ```bash
   pip install synapse-sdk[dashboard]
   ```

2. **포트 사용 가능성 확인**:
   ```bash
   # 포트 8080 사용 중인지 확인
   lsof -i :8080
   
   # 다른 포트 사용
   synapse devtools --port 8081
   ```

3. **프론트엔드 수동 빌드**:
   ```bash
   cd synapse_sdk/devtools/web
   npm install
   npm run build
   ```

### 프론트엔드 빌드 오류

**증상**: 프론트엔드 에셋 빌드가 실패합니다.

**해결방법**:

1. **Node.js 의존성 설치**:
   ```bash
   # Node.js 설치 (설치되지 않은 경우)
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   
   # 또는 nvm 사용
   nvm install 18
   nvm use 18
   ```

2. **npm 캐시 정리**:
   ```bash
   cd synapse_sdk/devtools/web
   rm -rf node_modules package-lock.json
   npm cache clean --force
   npm install
   ```

## 성능 문제

### 플러그인 실행 속도 저하

**증상**: 플러그인 실행 시간이 너무 오래 걸립니다.

**최적화 전략**:

1. **코드 프로파일링**:
   ```python
   import time
   
   def start(self):
       start_time = time.time()
       # 여기에 코드 작성
       self.run.log(f"Execution took {time.time() - start_time:.2f}s")
   ```

2. **병렬 처리 사용**:
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   def parallel_task(item):
       return process_item(item)
   
   def start(self):
       # 병렬로 항목 처리
       with ThreadPoolExecutor() as executor:
           results = list(executor.map(parallel_task, items))
   ```

3. **데이터 로딩 최적화**:
   ```python
   # 모든 것을 한 번에 로딩하는 대신
   data = pd.read_csv(large_file)
   
   # 청크 로딩 사용
   for chunk in pd.read_csv(large_file, chunksize=1000):
       process_chunk(chunk)
   ```

### 메모리 사용량 문제

**증상**: 높은 메모리 사용량 또는 메모리 부족 오류가 발생합니다.

**해결방법**:

1. **메모리 사용량 모니터링**:
   ```python
   import psutil
   
   def start(self):
       process = psutil.Process()
       self.run.log(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
   ```

2. **리스트 대신 제너레이터 사용**:
   ```python
   # 대신
   all_data = [process(item) for item in large_list]
   
   # 제너레이터 사용
   def process_items():
       for item in large_list:
           yield process(item)
   ```

3. **변수 명시적 정리**:
   ```python
   def start(self):
       large_data = load_data()
       result = process(large_data)
       del large_data  # 메모리 명시적 해제
       return result
   ```

## 로깅 및 디버깅

### 디버그 로깅 활성화

```bash
export SYNAPSE_DEBUG=true
export SYNAPSE_LOG_LEVEL=DEBUG
```

### 커스텀 로깅

```python
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def start(self):
    logger.debug("Starting plugin execution")
    # 여기에 코드 작성
```

### 디버깅 팁

1. **print 문 사용** (로그에 표시됨):
   ```python
   def start(self):
       print(f"Parameters: {self.params}")
       print(f"Working directory: {os.getcwd()}")
   ```

2. **파일 존재 확인**:
   ```python
   def start(self):
       file_path = self.params.input_file
       print(f"File exists: {os.path.exists(file_path)}")
       print(f"File size: {os.path.getsize(file_path)} bytes")
   ```

3. **데이터 타입 검증**:
   ```python
   def start(self):
       print(f"Parameter types: {type(self.params.input_data)}")
       print(f"Parameter value: {repr(self.params.input_data)}")
   ```

## 도움 받기

문제를 해결할 수 없는 경우:

1. **로그 철저히 확인**
2. **GitHub issues 검색**: https://github.com/datamaker/synapse-sdk/issues
3. **최소한의 재현 케이스** 생성
4. **Discord 커뮤니티 참여**: https://discord.gg/synapse-sdk
5. 자세한 오류 정보와 함께 **지원팀 문의**