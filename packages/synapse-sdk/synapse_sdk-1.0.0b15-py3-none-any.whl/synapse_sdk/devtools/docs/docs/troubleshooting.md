---
id: troubleshooting
title: Troubleshooting
sidebar_position: 10
---

# Troubleshooting

Common issues and their solutions when using Synapse SDK.

## Installation Issues

## Authentication Issues

### ClientError: 401 Unauthorized

**Symptoms**: API calls failing with 401 errors.

**Diagnosis Steps**:


3. **Verify token via CLI**:
   ```bash
   # Use the interactive config to check your token
   synapse config
   # Select "Show current configuration"
   # Tokens are now displayed in plain text for easy verification
   ```

4. **Verify token in code**:
   ```python
   from synapse_sdk.clients.backend import BackendClient
   
   client = BackendClient(
       base_url="https://api.synapse.sh",
       api_token="your-token"  # No "Token " prefix
   )
   
   try:
       user = client.get_current_user()
       print(f"Authenticated as: {user.email}")
   except Exception as e:
       print(f"Auth failed: {e}")
   ```

**Common Fixes**:
- Regenerate token from web interface
- Check token hasn't expired
- Verify correct backend URL

### Agent Authentication Errors

**Symptoms**: Agent-related operations failing.

**Solutions**:

1. **Check agent configuration**:
   ```bash
   synapse config
   # Select "Show current configuration"
   # Both backend and agent tokens are displayed in plain text
   ```

2. **Verify agent token**:
   ```python
   from synapse_sdk.clients.agent import AgentClient
   
   client = AgentClient(
       base_url="https://api.synapse.sh",
       agent_token="your-agent-token"
   )
   ```

## Connection Issues

### Connection Timeouts

**Symptoms**: Requests timing out or hanging.

**Solutions**:

1. **Increase timeout values**:
   ```python
   client = BackendClient(
       base_url="https://api.synapse.sh",
       api_token="your-token",
       timeout={'connect': 30, 'read': 120}
   )
   ```

2. **Check network connectivity**:
   ```bash
   # Test basic connectivity
   ping api.synapse.sh
   
   # Test HTTPS access
   curl -I https://api.synapse.sh/health
   ```

3. **Configure proxy if needed**:
   ```bash
   export HTTP_PROXY="http://proxy.company.com:8080"
   export HTTPS_PROXY="https://proxy.company.com:8080"
   ```

### DNS Resolution Issues

**Symptoms**: "Name or service not known" errors.

**Solutions**:

1. **Check DNS settings**:
   ```bash
   nslookup api.synapse.sh
   ```

2. **Try alternative DNS**:
   ```bash
   # Temporarily use Google DNS
   export SYNAPSE_BACKEND_HOST="$(dig @8.8.8.8 api.synapse.sh +short)"
   ```

3. **Use IP address directly** (temporary):
   ```python
   client = BackendClient(base_url="https://192.168.1.100:8000")
   ```

## Plugin Development Issues

### Plugin Import Errors

**Symptoms**: Plugins failing to load or import.

**Diagnosis**:
```bash
# Test plugin syntax
python -m py_compile plugin/__init__.py

# Check for circular imports
python -c "import plugin; print('OK')"
```

**Solutions**:

1. **Fix syntax errors**:
   ```bash
   # Use linting
   pip install ruff
   ruff check plugin/
   ```

2. **Check import paths**:
   ```python
   # In plugin/__init__.py
   from synapse_sdk.plugins.categories.base import Action, register_action
   # Not: from synapse_sdk.plugins.base import Action
   ```

3. **Verify plugin structure**:
   ```
   my-plugin/
   ├── config.yaml
   ├── plugin/
   │   └── __init__.py
   ├── requirements.txt
   └── README.md
   ```

### Plugin Execution Failures

**Symptoms**: Plugins starting but failing during execution.

**Debugging Steps**:

1. **Enable debug mode via CLI**:
   ```bash
   synapse
   # Select "Plugin Management"
   # Select "Run plugin locally"
   # Enter your action and parameters
   # Debug mode is enabled by default for local runs
   ```

2. **Enable debug mode manually**:
   ```bash
   export SYNAPSE_DEBUG=true
   synapse plugin run --path ./my-plugin --action test
   ```

2. **Check logs**:
   ```python
   def start(self):
       try:
           self.run.log("Starting plugin execution")
           # Your code here
           self.run.log("Plugin completed successfully")
       except Exception as e:
           self.run.log(f"Error: {str(e)}", level="ERROR")
           raise
   ```

3. **Validate parameters**:
   ```python
   from pydantic import ValidationError
   
   def start(self):
       try:
           # This will validate parameters
           params = self.params_model(**self.params)
       except ValidationError as e:
           self.run.log(f"Parameter validation failed: {e}")
           raise
   ```

### File Handling Issues

**Symptoms**: File operations failing in plugins.

**Common Issues & Solutions**:

1. **FileField not downloading**:
   ```python
   # Check file URL format
   class MyParams(BaseModel):
       input_file: FileField  # Expects URL
   
   def start(self):
       file_path = self.params.input_file
       if not os.path.exists(file_path):
           raise FileNotFoundError(f"File not found: {file_path}")
   ```

2. **Permission errors**:
   ```python
   import tempfile
   import shutil
   
   def start(self):
       # Use temporary directory
       with tempfile.TemporaryDirectory() as temp_dir:
           output_path = os.path.join(temp_dir, "result.csv")
           # Process and save to output_path
   ```

3. **Large file handling**:
   ```python
   def start(self):
       # Process in chunks for large files
       chunk_size = 1024 * 1024  # 1MB chunks
       with open(self.params.input_file, 'rb') as f:
           while True:
               chunk = f.read(chunk_size)
               if not chunk:
                   break
               process_chunk(chunk)
   ```

## Distributed Computing Issues

### Cluster Connection

**Symptoms**: Cannot connect to compute cluster.

**Solutions**:

1. **Check cluster status**:
   ```bash
   synapse cluster status
   # Should show cluster information
   ```

2. **Start local cluster**:
   ```bash
   synapse cluster start --dashboard-host=0.0.0.0
   ```

3. **Connect to remote cluster**:
   ```bash
   export SYNAPSE_CLUSTER_ADDRESS="cluster://remote-cluster:10001"
   synapse cluster status  # Should connect to remote cluster
   ```

### Memory Issues

**Symptoms**: Out of memory errors during execution.

**Solutions**:

1. **Increase memory allocation**:
   ```bash
   synapse cluster start --memory=2000000000  # 2GB
   ```

2. **Configure in code**:
   ```python
   from synapse_sdk.compute import init
   init(memory=2000000000)
   ```

3. **Process data in smaller chunks**:
   ```python
   def process_chunk(data_chunk):
       return process(data_chunk)
   
   # Split large data into chunks
   chunks = split_data(large_data)
   results = [process_chunk(chunk) for chunk in chunks]
   ```

### Job Failures

**Symptoms**: Jobs failing to start or complete.

**Solutions**:

1. **Check resource requirements**:
   ```python
   def my_task(resources={'cpus': 2, 'memory': '1GB'}):
       pass
   ```

2. **Verify runtime environment**:
   ```yaml
   # In plugin config.yaml
   runtime_env:
     pip:
       packages: ["pandas", "numpy"]
   ```

## Development Tools Issues

### Devtools Won't Start

**Symptoms**: `synapse --dev-tools` fails to start.

**Solutions**:

1. **Install dashboard dependencies**:
   ```bash
   pip install synapse-sdk[dashboard]
   ```

2. **Check port availability**:
   ```bash
   # Check if port 8080 is in use
   lsof -i :8080
   
   # Use different port
   synapse devtools --port 8081
   ```

3. **Build frontend manually**:
   ```bash
   cd synapse_sdk/devtools/web
   npm install
   npm run build
   ```

### Frontend Build Errors

**Symptoms**: Frontend assets failing to build.

**Solutions**:

1. **Install Node.js dependencies**:
   ```bash
   # Install Node.js (if not installed)
   curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
   sudo apt-get install -y nodejs
   
   # Or use nvm
   nvm install 18
   nvm use 18
   ```

2. **Clear npm cache**:
   ```bash
   cd synapse_sdk/devtools/web
   rm -rf node_modules package-lock.json
   npm cache clean --force
   npm install
   ```

## Performance Issues

### Slow Plugin Execution

**Symptoms**: Plugins taking too long to execute.

**Optimization Strategies**:

1. **Profile your code**:
   ```python
   import time
   
   def start(self):
       start_time = time.time()
       # Your code here
       self.run.log(f"Execution took {time.time() - start_time:.2f}s")
   ```

2. **Use parallel processing**:
   ```python
   from concurrent.futures import ThreadPoolExecutor
   
   def parallel_task(item):
       return process_item(item)
   
   def start(self):
       # Process items in parallel
       with ThreadPoolExecutor() as executor:
           results = list(executor.map(parallel_task, items))
   ```

3. **Optimize data loading**:
   ```python
   # Instead of loading everything at once
   data = pd.read_csv(large_file)
   
   # Use chunked loading
   for chunk in pd.read_csv(large_file, chunksize=1000):
       process_chunk(chunk)
   ```

### Memory Usage Issues

**Symptoms**: High memory usage or out-of-memory errors.

**Solutions**:

1. **Monitor memory usage**:
   ```python
   import psutil
   
   def start(self):
       process = psutil.Process()
       self.run.log(f"Memory usage: {process.memory_info().rss / 1024 / 1024:.1f} MB")
   ```

2. **Use generators instead of lists**:
   ```python
   # Instead of
   all_data = [process(item) for item in large_list]
   
   # Use generator
   def process_items():
       for item in large_list:
           yield process(item)
   ```

3. **Clear variables explicitly**:
   ```python
   def start(self):
       large_data = load_data()
       result = process(large_data)
       del large_data  # Free memory explicitly
       return result
   ```

## Logging and Debugging

### Enable Debug Logging

```bash
export SYNAPSE_DEBUG=true
export SYNAPSE_LOG_LEVEL=DEBUG
```

### Custom Logging

```python
import logging

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)

def start(self):
    logger.debug("Starting plugin execution")
    # Your code here
```

### Debugging Tips

1. **Use print statements** (they appear in logs):
   ```python
   def start(self):
       print(f"Parameters: {self.params}")
       print(f"Working directory: {os.getcwd()}")
   ```

2. **Check file existence**:
   ```python
   def start(self):
       file_path = self.params.input_file
       print(f"File exists: {os.path.exists(file_path)}")
       print(f"File size: {os.path.getsize(file_path)} bytes")
   ```

3. **Validate data types**:
   ```python
   def start(self):
       print(f"Parameter types: {type(self.params.input_data)}")
       print(f"Parameter value: {repr(self.params.input_data)}")
   ```

## Getting Help

If you can't resolve an issue:

1. **Check the logs** thoroughly
2. **Search GitHub issues**: https://github.com/datamaker/synapse-sdk/issues
3. **Create a minimal reproduction** case
4. **Join Discord community**: https://discord.gg/synapse-sdk
5. **Contact support** with detailed error information