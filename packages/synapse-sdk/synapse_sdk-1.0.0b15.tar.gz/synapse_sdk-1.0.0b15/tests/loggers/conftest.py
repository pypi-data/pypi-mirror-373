"""
Pytest configuration and fixtures for logger tests.
"""

import logging
import tempfile
from unittest.mock import Mock

import pytest


@pytest.fixture
def mock_logger():
    """Mock logger for testing."""
    mock_logger = Mock(spec=logging.Logger)
    mock_logger.info = Mock()
    mock_logger.warning = Mock()
    mock_logger.error = Mock()
    mock_logger.debug = Mock()
    mock_logger.critical = Mock()
    return mock_logger


@pytest.fixture
def temp_log_file():
    """Create a temporary log file for testing."""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.log', delete=False) as f:
        temp_path = f.name

    yield temp_path

    # Cleanup
    import os

    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_logging_config():
    """Mock logging configuration for testing."""
    return {
        'level': 'INFO',
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'handlers': ['console', 'file'],
    }


@pytest.fixture
def mock_log_record():
    """Mock log record for testing."""
    record = Mock(spec=logging.LogRecord)
    record.name = 'test_logger'
    record.levelno = logging.INFO
    record.levelname = 'INFO'
    record.pathname = '/test/path/test_file.py'
    record.lineno = 42
    record.msg = 'Test log message'
    record.args = ()
    record.exc_info = None
    record.funcName = 'test_function'
    record.created = 1640995200.0
    record.msecs = 123.456
    record.relativeCreated = 1000.0
    record.thread = 12345
    record.threadName = 'MainThread'
    record.processName = 'MainProcess'
    record.process = 67890
    record.getMessage = Mock(return_value='Test log message')
    return record


@pytest.fixture
def mock_log_handler():
    """Mock log handler for testing."""
    handler = Mock(spec=logging.Handler)
    handler.emit = Mock()
    handler.handle = Mock()
    handler.format = Mock(return_value='Formatted log message')
    return handler


@pytest.fixture
def mock_log_formatter():
    """Mock log formatter for testing."""
    formatter = Mock(spec=logging.Formatter)
    formatter.format = Mock(return_value='Formatted log message')
    return formatter


@pytest.fixture
def capture_logs(caplog):
    """Capture logs during test execution."""
    caplog.set_level(logging.DEBUG)
    return caplog


# Logger-specific markers
def pytest_configure(config):
    """Configure pytest for logger tests."""
    config.addinivalue_line('markers', 'logger: mark test as logger test')
    config.addinivalue_line('markers', 'handler: mark test as log handler test')
    config.addinivalue_line('markers', 'formatter: mark test as log formatter test')
    config.addinivalue_line('markers', 'level: mark test as log level test')
