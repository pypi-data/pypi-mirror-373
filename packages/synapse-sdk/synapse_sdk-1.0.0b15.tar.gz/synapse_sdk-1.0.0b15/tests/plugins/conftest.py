"""
Pytest configuration and fixtures for plugin tests.
"""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest


@pytest.fixture
def temp_plugin_dir():
    """Create a temporary directory for plugin testing."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_plugin_config():
    """Mock plugin configuration for testing."""
    return {
        'name': 'test_plugin',
        'version': '1.0.0',
        'description': 'A test plugin',
        'author': 'Test Author',
        'entry_points': {'synapse.plugins': 'test_plugin = test_plugin:main'},
    }


@pytest.fixture
def mock_plugin_manifest():
    """Mock plugin manifest for testing."""
    return {
        'plugin_id': 'test-plugin-123',
        'name': 'Test Plugin',
        'version': '1.0.0',
        'description': 'A test plugin for synapse',
        'author': 'Test Author',
        'dependencies': ['requests>=2.25.0'],
        'entry_points': ['upload', 'download'],
        'config_schema': {
            'type': 'object',
            'properties': {'api_key': {'type': 'string'}, 'endpoint': {'type': 'string'}},
        },
    }


@pytest.fixture
def mock_plugin_instance():
    """Mock plugin instance for testing."""
    plugin = Mock()
    plugin.name = 'test_plugin'
    plugin.version = '1.0.0'
    plugin.initialize = Mock(return_value=True)
    plugin.execute = Mock(return_value={'status': 'success'})
    plugin.cleanup = Mock()
    return plugin


@pytest.fixture
def mock_plugin_registry():
    """Mock plugin registry for testing."""
    registry = Mock()
    registry.plugins = {'test_plugin': Mock(), 'upload_plugin': Mock(), 'download_plugin': Mock()}
    registry.register = Mock()
    registry.unregister = Mock()
    registry.get_plugin = Mock()
    return registry


@pytest.fixture
def mock_plugin_loader():
    """Mock plugin loader for testing."""
    loader = Mock()
    loader.load_plugin = Mock(return_value=Mock())
    loader.unload_plugin = Mock()
    loader.list_plugins = Mock(return_value=['test_plugin'])
    return loader


@pytest.fixture
def temp_plugin_file(temp_plugin_dir):
    """Create a temporary plugin file for testing."""
    plugin_file = temp_plugin_dir / 'test_plugin.py'
    plugin_content = """
def main():
    return {"status": "success"}

def initialize(config):
    return True

def cleanup():
    pass
"""
    plugin_file.write_text(plugin_content)
    return plugin_file


@pytest.fixture
def mock_upload_plugin():
    """Mock upload plugin for testing."""
    plugin = Mock()
    plugin.name = 'upload_plugin'
    plugin.upload = Mock(return_value={'file_id': 'test-123'})
    plugin.validate_file = Mock(return_value=True)
    plugin.get_progress = Mock(return_value=0.5)
    return plugin


@pytest.fixture
def mock_download_plugin():
    """Mock download plugin for testing."""
    plugin = Mock()
    plugin.name = 'download_plugin'
    plugin.download = Mock(return_value={'local_path': '/tmp/file.txt'})
    plugin.validate_url = Mock(return_value=True)
    plugin.get_progress = Mock(return_value=0.75)
    return plugin


# Plugin-specific markers
def pytest_configure(config):
    """Configure pytest for plugin tests."""
    config.addinivalue_line('markers', 'plugin: mark test as plugin test')
    config.addinivalue_line('markers', 'upload: mark test as upload plugin test')
    config.addinivalue_line('markers', 'download: mark test as download plugin test')
    config.addinivalue_line('markers', 'registry: mark test as plugin registry test')
    config.addinivalue_line('markers', 'loader: mark test as plugin loader test')
