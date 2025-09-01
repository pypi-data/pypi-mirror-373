# Synapse SDK Test Configuration

This directory contains comprehensive pytest configurations for the Synapse SDK project.

## Test Structure

```
tests/
├── conftest.py                 # Main pytest configuration and shared fixtures
├── test_cli.py                 # CLI tests
├── test_cli_integration.py     # CLI integration tests
├── clients/
│   ├── conftest.py            # Client-specific fixtures
│   ├── test_backend_models.py
│   ├── test_base_client.py
│   └── test_collection_validators.py
├── utils/
│   ├── converters/
│   ├── storage/
│   │   ├── conftest.py        # Storage-specific fixtures
│   │   └── test_provider_selection.py
│   └── test_debug.py
├── loggers/
│   ├── conftest.py            # Logger-specific fixtures
│   └── test_base_logger.py
└── plugins/
    ├── conftest.py            # Plugin-specific fixtures
    └── upload/
```

## Configuration Files

### 1. pyproject.toml

Main pytest configuration with comprehensive settings for:

- Test discovery patterns
- Output formatting
- Markers for test categorization
- Warning filters
- Timeout settings

### 2. pytest.ini

Alternative configuration file with additional options:

- HTML and XML reporting
- Self-contained HTML reports
- JUnit XML output for CI tools

### 3. pytest-ci.ini

CI/CD optimized configuration with:

- Parallel test execution
- Coverage reporting with thresholds
- Optimized for automated environments

## Test Markers

The test suite uses markers to categorize tests:

### Core Markers

- `unit`: Fast, isolated unit tests
- `integration`: Slower tests with external dependencies
- `slow`: Tests that take significant time to run

### Component-Specific Markers

- `cli`: Command line interface tests
- `storage`: Storage provider tests
- `client`: Client tests
- `logger`: Logger tests
- `plugin`: Plugin tests

### Storage-Specific Markers

- `s3`: S3 storage tests
- `gcp`: GCP storage tests
- `sftp`: SFTP storage tests
- `http`: HTTP storage tests

### Client-Specific Markers

- `api`: API interaction tests
- `validation`: Validation tests

### Logger-Specific Markers

- `handler`: Log handler tests
- `formatter`: Log formatter tests
- `level`: Log level tests

### Plugin-Specific Markers

- `upload`: Upload plugin tests
- `download`: Download plugin tests
- `registry`: Plugin registry tests
- `loader`: Plugin loader tests

## Running Tests

### Basic Commands

```bash
# Run all tests
make test

# Run with coverage
make test-coverage

# Run only unit tests
make test-unit

# Run only integration tests
make test-integration
```

### Component-Specific Tests

```bash
# Run CLI tests
make test-cli

# Run storage tests
make test-storage

# Run client tests
make test-client

# Run logger tests
make test-logger

# Run plugin tests
make test-plugin
```

### Advanced Commands

```bash
# Run slow tests
make test-slow

# Run with verbose output
make test-verbose

# Run and stop on first failure
make test-failfast

# Clean test artifacts
make clean
```

### Using pytest directly

```bash
# Run specific test file
pytest tests/clients/test_base_client.py

# Run tests with specific marker
pytest -m "unit"

# Run tests excluding specific marker
pytest -m "not slow"

# Run tests with coverage
pytest --cov=synapse_sdk --cov-report=html

# Run tests in parallel
pytest -n auto

# Run tests with specific configuration
pytest -c pytest-ci.ini
```

## Fixtures

### Global Fixtures (conftest.py)

- `mock_devtools_config`: Temporary devtools configuration
- `empty_config`: Empty configuration file
- `mock_backend_config`: Standard backend configuration
- `mock_agent_list`: Standard agent list
- `mock_api_responses`: Standard API responses

### Storage Fixtures (tests/utils/storage/conftest.py)

- `mock_s3_credentials`: S3 credentials for testing
- `mock_gcp_credentials`: GCP credentials for testing
- `mock_sftp_credentials`: SFTP credentials for testing
- `mock_http_config`: HTTP storage configuration
- `temp_file`: Temporary file for testing
- `mock_storage_provider`: Mock storage provider
- `mock_fs`: Mock filesystem

### Client Fixtures (tests/clients/conftest.py)

- `mock_api_response`: Mock API response
- `mock_error_response`: Mock error response
- `mock_http_session`: Mock HTTP session
- `mock_requests_get/post/put/delete`: Mock HTTP requests
- `mock_backend_config`: Backend configuration
- `mock_collection_data`: Collection data
- `mock_validation_error`: Validation error

### Logger Fixtures (tests/loggers/conftest.py)

- `mock_logger`: Mock logger
- `temp_log_file`: Temporary log file
- `mock_logging_config`: Logging configuration
- `mock_log_record`: Log record
- `mock_log_handler`: Log handler
- `mock_log_formatter`: Log formatter
- `capture_logs`: Log capture fixture

### Plugin Fixtures (tests/plugins/conftest.py)

- `temp_plugin_dir`: Temporary plugin directory
- `mock_plugin_config`: Plugin configuration
- `mock_plugin_manifest`: Plugin manifest
- `mock_plugin_instance`: Plugin instance
- `mock_plugin_registry`: Plugin registry
- `mock_plugin_loader`: Plugin loader
- `temp_plugin_file`: Temporary plugin file
- `mock_upload_plugin`: Upload plugin
- `mock_download_plugin`: Download plugin

## Test Dependencies

The test suite requires the following packages (installed via `pip install -e .[test]`):

- `pytest>=7.0.0`: Core testing framework
- `pytest-cov>=4.0.0`: Coverage reporting
- `pytest-mock>=3.10.0`: Mocking utilities
- `pytest-timeout>=2.1.0`: Test timeout management
- `pytest-xdist>=3.0.0`: Parallel test execution
- `pytest-html>=3.1.0`: HTML test reports
- `pytest-json-report>=1.5.0`: JSON test reports

## Best Practices

### Writing Tests

1. Use appropriate markers to categorize tests
2. Use fixtures for common test data and mocks
3. Write descriptive test names
4. Keep tests isolated and independent
5. Use parametrized tests for similar test cases

### Test Organization

1. Group related tests in classes
2. Use descriptive file and directory names
3. Keep test files focused on specific functionality
4. Use conftest.py files for shared fixtures

### Running Tests

1. Run unit tests frequently during development
2. Run integration tests before commits
3. Use coverage reports to identify untested code
4. Use parallel execution for faster test runs in CI

## CI/CD Integration

The test suite is configured for CI/CD environments with:

- Parallel test execution
- Coverage reporting with thresholds
- JUnit XML output for CI tools
- Optimized settings for automated environments

Use `pytest-ci.ini` for CI/CD environments:

```bash
pytest -c pytest-ci.ini
```

## Troubleshooting

### Common Issues

1. **Import errors**: Ensure the package is installed in development mode
2. **Fixture not found**: Check if fixtures are in the correct conftest.py file
3. **Marker warnings**: Register custom markers in pytest_configure
4. **Timeout errors**: Increase timeout settings for slow tests

### Debugging

- Use `pytest --pdb` to drop into debugger on failures
- Use `pytest -vv` for verbose output
- Use `pytest --tb=long` for detailed tracebacks
- Use `pytest --lf` to run only the last failed tests
