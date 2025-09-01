"""Tests for plugin config utilities."""

import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from synapse_sdk.plugins.utils.config import (
    get_action_config,
    get_plugin_actions,
    get_plugin_metadata,
    read_plugin_config,
    validate_plugin_config,
)


class TestReadPluginConfig:
    """Test read_plugin_config function."""

    def test_read_config_from_current_directory(self):
        """Test reading config from current directory."""
        mock_config = {'name': 'test-plugin', 'actions': {'train': {}}}

        with patch('synapse_sdk.plugins.utils.config.get_dict_from_file') as mock_get_dict:
            mock_get_dict.return_value = mock_config

            result = read_plugin_config()

            mock_get_dict.assert_called_once_with('config.yaml')
            assert result == mock_config

    def test_read_config_from_plugin_path(self):
        """Test reading config from specific plugin path."""
        mock_config = {'name': 'test-plugin', 'actions': {'train': {}}}
        plugin_path = '/path/to/plugin'

        with patch('synapse_sdk.plugins.utils.config.get_dict_from_file') as mock_get_dict:
            mock_get_dict.return_value = mock_config

            result = read_plugin_config(plugin_path)

            expected_path = Path(plugin_path) / 'config.yaml'
            mock_get_dict.assert_called_once_with(expected_path)
            assert result == mock_config

    def test_read_config_file_not_found(self):
        """Test reading config when file doesn't exist."""
        with patch('synapse_sdk.plugins.utils.config.get_dict_from_file') as mock_get_dict:
            mock_get_dict.side_effect = FileNotFoundError('File not found')

            with pytest.raises(FileNotFoundError, match='Plugin config file not found'):
                read_plugin_config()

    def test_read_config_invalid_yaml(self):
        """Test reading config with invalid YAML."""
        with patch('synapse_sdk.plugins.utils.config.get_dict_from_file') as mock_get_dict:
            mock_get_dict.side_effect = ValueError('Invalid YAML')

            with pytest.raises(ValueError, match='Invalid plugin config file'):
                read_plugin_config()


class TestGetPluginActions:
    """Test get_plugin_actions function."""

    def test_get_actions_from_config(self):
        """Test getting actions from provided config."""
        config = {
            'name': 'test-plugin',
            'actions': {
                'train': {'entrypoint': 'plugin.train.TrainAction'},
                'inference': {'entrypoint': 'plugin.inference.InferenceAction'},
                'test': {'entrypoint': 'plugin.test.TestAction'},
            },
        }

        result = get_plugin_actions(config=config)

        assert result == ['train', 'inference', 'test']
        assert len(result) == 3

    def test_get_actions_from_plugin_path(self):
        """Test getting actions from plugin path."""
        config = {
            'actions': {
                'deploy': {'entrypoint': 'plugin.deploy.DeployAction'},
                'serve': {'entrypoint': 'plugin.serve.ServeAction'},
            }
        }

        with patch('synapse_sdk.plugins.utils.config.read_plugin_config') as mock_read:
            mock_read.return_value = config

            result = get_plugin_actions(plugin_path='/path/to/plugin')

            mock_read.assert_called_once_with('/path/to/plugin')
            assert result == ['deploy', 'serve']

    def test_get_actions_empty_actions(self):
        """Test getting actions when actions dict is empty."""
        config = {'name': 'test-plugin', 'actions': {}}

        result = get_plugin_actions(config=config)

        assert result == []

    def test_get_actions_no_config_or_path(self):
        """Test error when neither config nor path provided."""
        with pytest.raises(ValueError, match='Either config or plugin_path must be provided'):
            get_plugin_actions()

    def test_get_actions_missing_actions_key(self):
        """Test error when actions key is missing."""
        config = {'name': 'test-plugin'}

        with pytest.raises(KeyError, match="'actions' key not found"):
            get_plugin_actions(config=config)

    def test_get_actions_invalid_actions_type(self):
        """Test error when actions is not a dict."""
        config = {
            'name': 'test-plugin',
            'actions': ['train', 'test'],  # Should be dict, not list
        }

        with pytest.raises(ValueError, match="'actions' must be a dictionary"):
            get_plugin_actions(config=config)


class TestGetActionConfig:
    """Test get_action_config function."""

    def test_get_action_config_success(self):
        """Test getting action config successfully."""
        config = {
            'actions': {
                'train': {'entrypoint': 'plugin.train.TrainAction', 'method': 'job', 'description': 'Train a model'},
                'inference': {'entrypoint': 'plugin.inference.InferenceAction', 'method': 'restapi'},
            }
        }

        result = get_action_config('train', config=config)

        expected = {'entrypoint': 'plugin.train.TrainAction', 'method': 'job', 'description': 'Train a model'}
        assert result == expected

    def test_get_action_config_from_path(self):
        """Test getting action config from plugin path."""
        config = {'actions': {'test': {'entrypoint': 'plugin.test.TestAction'}}}

        with patch('synapse_sdk.plugins.utils.config.read_plugin_config') as mock_read:
            mock_read.return_value = config

            result = get_action_config('test', plugin_path='/path/to/plugin')

            mock_read.assert_called_once_with('/path/to/plugin')
            assert result == {'entrypoint': 'plugin.test.TestAction'}

    def test_get_action_config_action_not_found(self):
        """Test error when action is not found."""
        config = {
            'actions': {
                'train': {'entrypoint': 'plugin.train.TrainAction'},
                'test': {'entrypoint': 'plugin.test.TestAction'},
            }
        }

        with pytest.raises(KeyError, match="Action 'nonexistent' not found. Available actions: \\['train', 'test'\\]"):
            get_action_config('nonexistent', config=config)

    def test_get_action_config_no_actions_key(self):
        """Test error when actions key is missing."""
        config = {'name': 'test-plugin'}

        with pytest.raises(KeyError, match="'actions' key not found"):
            get_action_config('train', config=config)


class TestValidatePluginConfig:
    """Test validate_plugin_config function."""

    def test_validate_valid_config(self):
        """Test validation of valid config."""
        config = {
            'name': 'Test Plugin',
            'code': 'test-plugin',
            'version': '1.0.0',
            'category': 'neural_net',
            'actions': {'train': {'entrypoint': 'plugin.train.TrainAction'}},
        }

        result = validate_plugin_config(config)

        assert result is True

    def test_validate_missing_required_field(self):
        """Test validation error for missing required field."""
        config = {
            'name': 'Test Plugin',
            'code': 'test-plugin',
            # missing version
            'category': 'neural_net',
            'actions': {'train': {'entrypoint': 'plugin.train.TrainAction'}},
        }

        with pytest.raises(ValueError, match="Required field 'version' missing"):
            validate_plugin_config(config)

    def test_validate_invalid_actions_type(self):
        """Test validation error for invalid actions type."""
        config = {
            'name': 'Test Plugin',
            'code': 'test-plugin',
            'version': '1.0.0',
            'category': 'neural_net',
            'actions': 'invalid',  # Should be dict
        }

        with pytest.raises(ValueError, match="'actions' must be a dictionary"):
            validate_plugin_config(config)

    def test_validate_empty_actions(self):
        """Test validation error for empty actions."""
        config = {
            'name': 'Test Plugin',
            'code': 'test-plugin',
            'version': '1.0.0',
            'category': 'neural_net',
            'actions': {},
        }

        with pytest.raises(ValueError, match='Plugin must define at least one action'):
            validate_plugin_config(config)

    def test_validate_invalid_action_config(self):
        """Test validation error for invalid action config."""
        config = {
            'name': 'Test Plugin',
            'code': 'test-plugin',
            'version': '1.0.0',
            'category': 'neural_net',
            'actions': {
                'train': 'invalid'  # Should be dict
            },
        }

        with pytest.raises(ValueError, match="Action 'train' configuration must be a dictionary"):
            validate_plugin_config(config)

    def test_validate_missing_entrypoint(self):
        """Test validation error for missing entrypoint."""
        config = {
            'name': 'Test Plugin',
            'code': 'test-plugin',
            'version': '1.0.0',
            'category': 'neural_net',
            'actions': {
                'train': {}  # Missing entrypoint
            },
        }

        with pytest.raises(ValueError, match="Action 'train' missing required 'entrypoint' field"):
            validate_plugin_config(config)

    def test_validate_restapi_without_entrypoint(self):
        """Test validation allows restapi actions without entrypoint."""
        config = {
            'name': 'Test Plugin',
            'code': 'test-plugin',
            'version': '1.0.0',
            'category': 'neural_net',
            'actions': {
                'api': {'method': 'restapi'}  # No entrypoint needed for restapi
            },
        }

        result = validate_plugin_config(config)

        assert result is True

    def test_validate_invalid_category(self):
        """Test validation error for invalid category."""
        config = {
            'name': 'Test Plugin',
            'code': 'test-plugin',
            'version': '1.0.0',
            'category': 'invalid_category',
            'actions': {'train': {'entrypoint': 'plugin.train.TrainAction'}},
        }

        with pytest.raises(ValueError, match="Invalid category 'invalid_category'"):
            validate_plugin_config(config)


class TestGetPluginMetadata:
    """Test get_plugin_metadata function."""

    def test_get_metadata_from_config(self):
        """Test getting metadata from provided config."""
        config = {
            'name': 'Test Plugin',
            'code': 'test-plugin',
            'version': '1.0.0',
            'category': 'neural_net',
            'description': 'A test plugin',
            'actions': {'train': {}},
            'extra_field': 'ignored',
        }

        result = get_plugin_metadata(config=config)

        expected = {
            'name': 'Test Plugin',
            'code': 'test-plugin',
            'version': '1.0.0',
            'category': 'neural_net',
            'description': 'A test plugin',
        }
        assert result == expected

    def test_get_metadata_partial_fields(self):
        """Test getting metadata with missing optional fields."""
        config = {
            'name': 'Test Plugin',
            'code': 'test-plugin',
            'version': '1.0.0',
            # missing description and category
            'actions': {'train': {}},
        }

        result = get_plugin_metadata(config=config)

        expected = {'name': 'Test Plugin', 'code': 'test-plugin', 'version': '1.0.0'}
        assert result == expected

    def test_get_metadata_from_path(self):
        """Test getting metadata from plugin path."""
        config = {'name': 'Test Plugin', 'code': 'test-plugin', 'version': '1.0.0', 'category': 'export'}

        with patch('synapse_sdk.plugins.utils.config.read_plugin_config') as mock_read:
            mock_read.return_value = config

            result = get_plugin_metadata(plugin_path='/path/to/plugin')

            mock_read.assert_called_once_with('/path/to/plugin')
            expected = {'name': 'Test Plugin', 'code': 'test-plugin', 'version': '1.0.0', 'category': 'export'}
            assert result == expected

    def test_get_metadata_no_config_or_path(self):
        """Test error when neither config nor path provided."""
        with pytest.raises(ValueError, match='Either config or plugin_path must be provided'):
            get_plugin_metadata()


# Integration tests with real files
class TestPluginConfigIntegration:
    """Integration tests using real config files."""

    def test_read_real_config_file(self):
        """Test reading a real config file."""
        config_content = """
name: "Test Plugin"
code: "test-plugin"
version: "1.0.0"
category: "neural_net"
description: "A test plugin for integration testing"
actions:
  train:
    entrypoint: "plugin.train.TrainAction"
    method: "job"
  inference:
    entrypoint: "plugin.inference.InferenceAction"
    method: "restapi"
  test:
    entrypoint: "plugin.test.TestAction"
"""

        with tempfile.TemporaryDirectory() as temp_dir:
            config_path = Path(temp_dir) / 'config.yaml'
            config_path.write_text(config_content)

            # Test reading config
            config = read_plugin_config(temp_dir)

            # Test getting actions
            actions = get_plugin_actions(config=config)
            assert set(actions) == {'train', 'inference', 'test'}

            # Test getting specific action config
            train_config = get_action_config('train', config=config)
            assert train_config['entrypoint'] == 'plugin.train.TrainAction'
            assert train_config['method'] == 'job'

            # Test validation
            assert validate_plugin_config(config) is True

            # Test metadata
            metadata = get_plugin_metadata(config=config)
            assert metadata['name'] == 'Test Plugin'
            assert metadata['code'] == 'test-plugin'
            assert metadata['version'] == '1.0.0'
