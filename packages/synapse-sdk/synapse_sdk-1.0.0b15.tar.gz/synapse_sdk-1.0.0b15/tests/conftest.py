"""
Pytest configuration and shared fixtures for CLI tests
"""

import json
import os
import tempfile
from unittest.mock import patch

import pytest


@pytest.fixture
def mock_devtools_config():
    """Create a temporary devtools config for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        config = {
            'backend': {'host': 'https://api.synapse.sh', 'token': 'test-token-123'},
            'agent': {'id': 'test-agent-123', 'name': 'Test Agent'},
        }
        json.dump(config, f)
        temp_path = f.name

    # Patch the config file path
    with patch('synapse_sdk.devtools.config.DEVTOOLS_CONFIG_FILE', temp_path):
        yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def empty_config():
    """Create an empty config file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
        json.dump({}, f)
        temp_path = f.name

    with patch('synapse_sdk.devtools.config.DEVTOOLS_CONFIG_FILE', temp_path):
        yield temp_path

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def mock_backend_config():
    """Standard backend configuration for testing"""
    return {'host': 'https://api.synapse.sh', 'token': 'test-token-abc123'}


@pytest.fixture
def mock_agent_list():
    """Standard agent list for testing"""
    return [
        {
            'id': 'agent-prod-001',
            'name': 'Production Agent',
            'url': 'http://prod-agent.example.com:8000',
            'status_display': 'online',
        },
        {
            'id': 'agent-dev-002',
            'name': 'Development Agent',
            'url': 'http://dev-agent.example.com:8000',
            'status_display': 'offline',
        },
        {
            'id': 'agent-test-003',
            'name': 'Test Agent',
            'url': 'http://test-agent.example.com:8000',
            'status_display': 'online',
        },
    ]


@pytest.fixture
def mock_api_responses(mock_backend_config, mock_agent_list):
    """Standard API responses for testing"""
    return {
        'users_me': {'tenants': [{'code': 'test-tenant-123'}]},
        'agents': {'results': mock_agent_list},
        'health': {'status': 'healthy', 'timestamp': '2024-01-01T00:00:00Z'},
    }


# Configure pytest to show full diff for assertions
def pytest_configure(config):
    """Configure pytest settings"""
    config.addinivalue_line('markers', 'integration: mark test as integration test')
    config.addinivalue_line('markers', 'unit: mark test as unit test')
    config.addinivalue_line('markers', 'slow: mark test as slow running')


# Custom assertion helpers
def assert_config_file_contains(config_path, expected_config):
    """Assert that config file contains expected configuration"""
    with open(config_path, 'r') as f:
        actual_config = json.load(f)

    for key, value in expected_config.items():
        assert key in actual_config
        if isinstance(value, dict):
            for subkey, subvalue in value.items():
                assert subkey in actual_config[key]
                assert actual_config[key][subkey] == subvalue
        else:
            assert actual_config[key] == value


# Test data generators
def generate_test_agents(count=3):
    """Generate test agent data"""
    agents = []
    for i in range(count):
        agents.append({
            'id': f'agent-{i:03d}',
            'name': f'Test Agent {i + 1}',
            'url': f'http://agent{i + 1}.example.com:8000',
            'status_display': 'online' if i % 2 == 0 else 'offline',
        })
    return agents


def generate_api_error_responses():
    """Generate common API error responses for testing"""
    return {
        '401': {'detail': 'Invalid authentication credentials'},
        '403': {'detail': 'Permission denied'},
        '404': {'detail': 'Not found'},
        '500': {'detail': 'Internal server error'},
        'timeout': 'Connection timeout',
        'connection_error': 'Connection failed',
    }
