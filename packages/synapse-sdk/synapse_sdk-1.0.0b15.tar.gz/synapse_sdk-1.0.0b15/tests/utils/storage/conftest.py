"""
Pytest configuration and fixtures for storage tests.
"""

import tempfile
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_s3_credentials():
    """Mock S3 credentials for testing."""
    return {
        'access_key': 'test-access-key',
        'secret_key': 'test-secret-key',
        'bucket': 'test-bucket',
        'region': 'us-east-1',
    }


@pytest.fixture
def mock_gcp_credentials():
    """Mock GCP credentials for testing."""
    return {'token': 'test-token', 'bucket': 'test-bucket', 'project': 'test-project'}


@pytest.fixture
def mock_sftp_credentials():
    """Mock SFTP credentials for testing."""
    return {'username': 'test-user', 'password': 'test-password', 'host': 'test-host.com', 'port': 22}


@pytest.fixture
def mock_http_config():
    """Mock HTTP storage configuration for testing."""
    return {'base_url': 'https://api.example.com', 'headers': {'Authorization': 'Bearer test-token'}}


@pytest.fixture
def temp_file():
    """Create a temporary file for testing."""
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b'test content')
        temp_path = f.name

    yield temp_path

    # Cleanup
    import os

    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_storage_provider():
    """Mock storage provider for testing."""
    mock_provider = Mock()
    mock_provider.upload.return_value = True
    mock_provider.download.return_value = True
    mock_provider.delete.return_value = True
    mock_provider.exists.return_value = True
    return mock_provider


@pytest.fixture
def mock_fs():
    """Mock filesystem for testing."""
    with patch('fsspec.filesystem') as mock_fs:
        mock_fs.return_value = Mock()
        yield mock_fs


# Storage-specific markers
def pytest_configure(config):
    """Configure pytest for storage tests."""
    config.addinivalue_line('markers', 'storage: mark test as storage provider test')
    config.addinivalue_line('markers', 's3: mark test as S3 storage test')
    config.addinivalue_line('markers', 'gcp: mark test as GCP storage test')
    config.addinivalue_line('markers', 'sftp: mark test as SFTP storage test')
    config.addinivalue_line('markers', 'http: mark test as HTTP storage test')
