"""Tests for plugin action utilities."""

import json
from unittest.mock import MagicMock, patch

import pytest

from synapse_sdk.plugins.utils.actions import (
    get_action,
    get_action_class,
    get_available_actions,
    is_action_available,
)


class TestGetActionClass:
    """Test get_action_class function."""

    @patch('synapse_sdk.plugins.utils.actions.register_actions')
    @patch('synapse_sdk.plugins.utils.actions._REGISTERED_ACTIONS')
    def test_get_action_class_success(self, mock_registered, mock_register):
        """Test successfully getting an action class."""
        mock_action_class = MagicMock()
        mock_registered.__getitem__.return_value = {'train': mock_action_class}

        result = get_action_class('neural_net', 'train')

        mock_register.assert_called_once()
        assert result == mock_action_class

    @patch('synapse_sdk.plugins.utils.actions.register_actions')
    @patch('synapse_sdk.plugins.utils.actions._REGISTERED_ACTIONS')
    def test_get_action_class_invalid_category(self, mock_registered, mock_register):
        """Test error when category doesn't exist."""
        mock_registered.__getitem__.side_effect = KeyError('invalid_category')
        mock_registered.keys.return_value = ['neural_net', 'export']

        with pytest.raises(
            KeyError, match="Category 'invalid_category' not found. Available categories: \\['neural_net', 'export'\\]"
        ):
            get_action_class('invalid_category', 'train')

    @patch('synapse_sdk.plugins.utils.actions.register_actions')
    @patch('synapse_sdk.plugins.utils.actions._REGISTERED_ACTIONS')
    def test_get_action_class_invalid_action(self, mock_registered, mock_register):
        """Test error when action doesn't exist in category."""
        mock_category_actions = {'train': MagicMock(), 'test': MagicMock()}
        mock_registered.__getitem__.return_value = mock_category_actions
        mock_registered.__contains__.return_value = True

        with pytest.raises(
            KeyError,
            match="Action 'invalid_action' not found in category 'neural_net'. "
            "Available actions: \\['train', 'test'\\]",
        ):
            get_action_class('neural_net', 'invalid_action')


class TestGetAvailableActions:
    """Test get_available_actions function."""

    @patch('synapse_sdk.plugins.utils.actions.register_actions')
    @patch('synapse_sdk.plugins.utils.actions._REGISTERED_ACTIONS')
    def test_get_available_actions_success(self, mock_registered, mock_register):
        """Test successfully getting available actions."""
        mock_actions = {'train': MagicMock(), 'inference': MagicMock(), 'test': MagicMock()}
        mock_registered.__getitem__.return_value = mock_actions
        mock_registered.__contains__.return_value = True

        result = get_available_actions('neural_net')

        mock_register.assert_called_once()
        assert set(result) == {'train', 'inference', 'test'}

    @patch('synapse_sdk.plugins.utils.actions.register_actions')
    @patch('synapse_sdk.plugins.utils.actions._REGISTERED_ACTIONS')
    def test_get_available_actions_invalid_category(self, mock_registered, mock_register):
        """Test error when category doesn't exist."""
        mock_registered.__contains__.return_value = False
        mock_registered.keys.return_value = ['neural_net', 'export']

        with pytest.raises(
            KeyError, match="Category 'invalid_category' not found. Available categories: \\['neural_net', 'export'\\]"
        ):
            get_available_actions('invalid_category')


class TestIsActionAvailable:
    """Test is_action_available function."""

    @patch('synapse_sdk.plugins.utils.actions.get_available_actions')
    def test_is_action_available_true(self, mock_get_actions):
        """Test when action is available."""
        mock_get_actions.return_value = ['train', 'inference', 'test']

        result = is_action_available('neural_net', 'train')

        assert result is True
        mock_get_actions.assert_called_once_with('neural_net')

    @patch('synapse_sdk.plugins.utils.actions.get_available_actions')
    def test_is_action_available_false(self, mock_get_actions):
        """Test when action is not available."""
        mock_get_actions.return_value = ['train', 'inference', 'test']

        result = is_action_available('neural_net', 'nonexistent')

        assert result is False
        mock_get_actions.assert_called_once_with('neural_net')

    @patch('synapse_sdk.plugins.utils.actions.get_available_actions')
    def test_is_action_available_invalid_category(self, mock_get_actions):
        """Test when category doesn't exist."""
        mock_get_actions.side_effect = KeyError('Category not found')

        result = is_action_available('invalid_category', 'train')

        assert result is False


class TestGetAction:
    """Test get_action function."""

    @patch('synapse_sdk.plugins.utils.actions.get_action_class')
    @patch('synapse_sdk.plugins.utils.actions.read_plugin_config')
    def test_get_action_with_dict_params(self, mock_read_config, mock_get_class):
        """Test getting action with dictionary parameters."""
        mock_config = {'category': 'neural_net'}
        mock_read_config.return_value = mock_config
        mock_action_instance = MagicMock()
        mock_action_class = MagicMock(return_value=mock_action_instance)
        mock_get_class.return_value = mock_action_class

        params = {'dataset_path': '/data', 'epochs': 10}

        result = get_action('train', params)

        mock_read_config.assert_called_once()
        mock_get_class.assert_called_once_with('neural_net', 'train')
        mock_action_class.assert_called_once_with(params, mock_config)
        assert result == mock_action_instance

    @patch('synapse_sdk.plugins.utils.actions.get_action_class')
    @patch('synapse_sdk.plugins.utils.actions.read_plugin_config')
    def test_get_action_with_json_string_params(self, mock_read_config, mock_get_class):
        """Test getting action with JSON string parameters."""
        mock_config = {'category': 'export'}
        mock_read_config.return_value = mock_config
        mock_action_instance = MagicMock()
        mock_action_class = MagicMock(return_value=mock_action_instance)
        mock_get_class.return_value = mock_action_class

        params_dict = {'output_format': 'csv', 'destination': '/output'}
        params_json = json.dumps(params_dict)

        result = get_action('export', params_json)

        mock_action_class.assert_called_once_with(params_dict, mock_config)
        assert result == mock_action_instance

    @patch('synapse_sdk.plugins.utils.actions.get_action_class')
    @patch('synapse_sdk.plugins.utils.actions.read_plugin_config')
    @patch('synapse_sdk.plugins.utils.actions.get_dict_from_file')
    def test_get_action_with_file_params(self, mock_get_dict, mock_read_config, mock_get_class):
        """Test getting action with file path parameters."""
        mock_config = {'category': 'upload'}
        mock_read_config.return_value = mock_config
        mock_params = {'bucket': 's3://my-bucket', 'files': ['file1.txt']}
        mock_get_dict.return_value = mock_params
        mock_action_instance = MagicMock()
        mock_action_class = MagicMock(return_value=mock_action_instance)
        mock_get_class.return_value = mock_action_class

        # Simulate JSON decode error to trigger file reading
        with patch('json.loads', side_effect=json.JSONDecodeError('Invalid JSON', '', 0)):
            result = get_action('upload', '/path/to/params.yaml')

        mock_get_dict.assert_called_once_with('/path/to/params.yaml')
        mock_action_class.assert_called_once_with(mock_params, mock_config)
        assert result == mock_action_instance

    @patch('synapse_sdk.plugins.utils.actions.get_action_class')
    @patch('synapse_sdk.plugins.utils.actions.read_plugin_config')
    def test_get_action_with_config_dict(self, mock_read_config, mock_get_class):
        """Test getting action with provided config dictionary."""
        provided_config = {'category': 'smart_tool', 'name': 'Test Plugin'}
        mock_action_instance = MagicMock()
        mock_action_class = MagicMock(return_value=mock_action_instance)
        mock_get_class.return_value = mock_action_class

        params = {'input_data': '/data'}

        result = get_action('auto_label', params, config=provided_config)

        # Should not call read_plugin_config since config was provided
        mock_read_config.assert_not_called()
        mock_get_class.assert_called_once_with('smart_tool', 'auto_label')
        mock_action_class.assert_called_once_with(params, provided_config)
        assert result == mock_action_instance

    @patch('synapse_sdk.plugins.utils.actions.get_action_class')
    @patch('synapse_sdk.plugins.utils.actions.read_plugin_config')
    def test_get_action_with_config_path(self, mock_read_config, mock_get_class):
        """Test getting action with config file path."""
        mock_config = {'category': 'data_validation'}
        mock_read_config.return_value = mock_config
        mock_action_instance = MagicMock()
        mock_action_class = MagicMock(return_value=mock_action_instance)
        mock_get_class.return_value = mock_action_class

        params = {'data_path': '/data'}
        config_path = '/path/to/plugin'

        result = get_action('validation', params, config=config_path)

        mock_read_config.assert_called_once_with(plugin_path=config_path)
        mock_get_class.assert_called_once_with('data_validation', 'validation')
        mock_action_class.assert_called_once_with(params, mock_config)
        assert result == mock_action_instance

    @patch('synapse_sdk.plugins.utils.actions.get_action_class')
    @patch('synapse_sdk.plugins.utils.actions.read_plugin_config')
    def test_get_action_with_additional_args(self, mock_read_config, mock_get_class):
        """Test getting action with additional arguments."""
        mock_config = {'category': 'neural_net'}
        mock_read_config.return_value = mock_config
        mock_action_instance = MagicMock()
        mock_action_class = MagicMock(return_value=mock_action_instance)
        mock_get_class.return_value = mock_action_class

        params = {'dataset_path': '/data'}
        additional_args = ('arg1', 'arg2')
        additional_kwargs = {'debug': True, 'job_id': 'test-job'}

        result = get_action('train', params, *additional_args, **additional_kwargs)

        mock_action_class.assert_called_once_with(params, mock_config, *additional_args, **additional_kwargs)
        assert result == mock_action_instance
