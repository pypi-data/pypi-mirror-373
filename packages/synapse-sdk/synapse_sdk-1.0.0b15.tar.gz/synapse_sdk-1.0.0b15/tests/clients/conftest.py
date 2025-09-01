"""
Pytest configuration and fixtures for client tests.
"""

import json
from unittest.mock import Mock, patch

import pytest


@pytest.fixture
def mock_api_response():
    """Mock API response for testing."""
    return {
        'status': 'success',
        'data': {'id': 'test-id', 'name': 'test-name'},
        'message': 'Operation completed successfully',
    }


@pytest.fixture
def mock_error_response():
    """Mock error response for testing."""
    return {'status': 'error', 'error': 'Test error message', 'code': 400}


@pytest.fixture
def mock_http_session():
    """Mock HTTP session for testing."""
    with patch('requests.Session') as mock_session:
        mock_session.return_value = Mock()
        yield mock_session


@pytest.fixture
def mock_requests_get():
    """Mock requests.get for testing."""
    with patch('requests.get') as mock_get:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'data': 'test'}
        mock_response.text = json.dumps({'data': 'test'})
        mock_get.return_value = mock_response
        yield mock_get


@pytest.fixture
def mock_requests_post():
    """Mock requests.post for testing."""
    with patch('requests.post') as mock_post:
        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {'id': 'new-id'}
        mock_response.text = json.dumps({'id': 'new-id'})
        mock_post.return_value = mock_response
        yield mock_post


@pytest.fixture
def mock_requests_put():
    """Mock requests.put for testing."""
    with patch('requests.put') as mock_put:
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {'updated': True}
        mock_response.text = json.dumps({'updated': True})
        mock_put.return_value = mock_response
        yield mock_put


@pytest.fixture
def mock_requests_delete():
    """Mock requests.delete for testing."""
    with patch('requests.delete') as mock_delete:
        mock_response = Mock()
        mock_response.status_code = 204
        mock_response.text = ''
        mock_delete.return_value = mock_response
        yield mock_delete


@pytest.fixture
def mock_backend_config():
    """Mock backend configuration for testing."""
    return {'host': 'https://api.synapse.sh', 'token': 'test-token-123', 'timeout': 30, 'retries': 3}


@pytest.fixture
def mock_collection_data():
    """Mock collection data for testing."""
    return {
        'id': 'collection-123',
        'name': 'Test Collection',
        'description': 'A test collection',
        'created_at': '2024-01-01T00:00:00Z',
        'updated_at': '2024-01-01T00:00:00Z',
        'metadata': {'key': 'value'},
    }


@pytest.fixture
def mock_validation_error():
    """Mock validation error for testing."""
    return {'detail': [{'loc': ['body', 'name'], 'msg': 'field required', 'type': 'value_error.missing'}]}


# Client-specific markers
def pytest_configure(config):
    """Configure pytest for client tests."""
    config.addinivalue_line('markers', 'client: mark test as client test')
    config.addinivalue_line('markers', 'api: mark test as API interaction test')
    config.addinivalue_line('markers', 'validation: mark test as validation test')
    config.addinivalue_line('markers', 'http: mark test as HTTP request test')
