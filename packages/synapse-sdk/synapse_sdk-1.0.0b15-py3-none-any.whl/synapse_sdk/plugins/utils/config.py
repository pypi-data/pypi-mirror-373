"""Plugin configuration utilities."""

from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from synapse_sdk.utils.file import get_dict_from_file


def read_plugin_config(plugin_path: Optional[Union[str, Path]] = None) -> Dict[str, Any]:
    """Read plugin configuration from config.yaml file.

    Args:
        plugin_path: Path to plugin directory. If None, looks for config.yaml in current directory.

    Returns:
        Dict containing plugin configuration.

    Raises:
        FileNotFoundError: If config.yaml file is not found.
        ValueError: If config.yaml is invalid.
    """
    config_file_name = 'config.yaml'
    if plugin_path:
        config_path = Path(plugin_path) / config_file_name
    else:
        config_path = config_file_name

    try:
        return get_dict_from_file(config_path)
    except FileNotFoundError:
        raise FileNotFoundError(f'Plugin config file not found: {config_path}')
    except Exception as e:
        raise ValueError(f'Invalid plugin config file: {e}')


def get_plugin_actions(
    config: Optional[Dict[str, Any]] = None, plugin_path: Optional[Union[str, Path]] = None
) -> List[str]:
    """Get list of action names from plugin configuration.

    Args:
        config: Plugin configuration dictionary. If None, reads from plugin_path.
        plugin_path: Path to plugin directory. Used if config is None.

    Returns:
        List of action names defined in the plugin.

    Raises:
        ValueError: If neither config nor plugin_path is provided.
        KeyError: If 'actions' key is missing from config.

    Examples:
        >>> get_plugin_actions(plugin_path="./my-plugin")
        ['train', 'inference', 'test']

        >>> config = {'actions': {'train': {...}, 'test': {...}}}
        >>> get_plugin_actions(config=config)
        ['train', 'test']
    """
    if config is None:
        if plugin_path is None:
            raise ValueError('Either config or plugin_path must be provided')
        config = read_plugin_config(plugin_path)

    if 'actions' not in config:
        raise KeyError("'actions' key not found in plugin configuration")

    actions = config['actions']
    if not isinstance(actions, dict):
        raise ValueError("'actions' must be a dictionary")

    return list(actions.keys())


def get_action_config(
    action_name: str, config: Optional[Dict[str, Any]] = None, plugin_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """Get configuration for a specific action.

    Args:
        action_name: Name of the action to get config for.
        config: Plugin configuration dictionary. If None, reads from plugin_path.
        plugin_path: Path to plugin directory. Used if config is None.

    Returns:
        Dictionary containing action configuration.

    Raises:
        ValueError: If neither config nor plugin_path is provided.
        KeyError: If action is not found in plugin configuration.

    Examples:
        >>> get_action_config('train', plugin_path="./my-plugin")
        {'entrypoint': 'plugin.train.TrainAction', 'method': 'job'}
    """
    if config is None:
        if plugin_path is None:
            raise ValueError('Either config or plugin_path must be provided')
        config = read_plugin_config(plugin_path)

    if 'actions' not in config:
        raise KeyError("'actions' key not found in plugin configuration")

    actions = config['actions']
    if action_name not in actions:
        available_actions = list(actions.keys())
        raise KeyError(f"Action '{action_name}' not found. Available actions: {available_actions}")

    return actions[action_name]


def validate_plugin_config(config: Dict[str, Any]) -> bool:
    """Validate plugin configuration structure.

    Args:
        config: Plugin configuration dictionary to validate.

    Returns:
        True if configuration is valid.

    Raises:
        ValueError: If configuration is invalid with detailed error message.

    Examples:
        >>> config = {
        ...     'name': 'My Plugin',
        ...     'code': 'my-plugin',
        ...     'version': '1.0.0',
        ...     'category': 'neural_net',
        ...     'actions': {'train': {'entrypoint': 'plugin.train.TrainAction'}}
        ... }
        >>> validate_plugin_config(config)
        True
    """
    required_fields = ['name', 'code', 'version', 'category', 'actions']

    # Check required fields
    for field in required_fields:
        if field not in config:
            raise ValueError(f"Required field '{field}' missing from plugin configuration")

    # Validate actions structure
    actions = config['actions']
    if not isinstance(actions, dict):
        raise ValueError("'actions' must be a dictionary")

    if not actions:
        raise ValueError('Plugin must define at least one action')

    # Validate each action
    for action_name, action_config in actions.items():
        if not isinstance(action_config, dict):
            raise ValueError(f"Action '{action_name}' configuration must be a dictionary")

        # Check for entrypoint (required for most actions)
        if 'entrypoint' not in action_config and action_config.get('method') != 'restapi':
            raise ValueError(f"Action '{action_name}' missing required 'entrypoint' field")

    # Validate category
    from synapse_sdk.plugins.enums import PluginCategory

    valid_categories = [cat.value for cat in PluginCategory]
    if config['category'] not in valid_categories:
        raise ValueError(f"Invalid category '{config['category']}'. Must be one of: {valid_categories}")

    return True


def get_plugin_metadata(
    config: Optional[Dict[str, Any]] = None, plugin_path: Optional[Union[str, Path]] = None
) -> Dict[str, Any]:
    """Get plugin metadata (name, version, description, etc.).

    Args:
        config: Plugin configuration dictionary. If None, reads from plugin_path.
        plugin_path: Path to plugin directory. Used if config is None.

    Returns:
        Dictionary containing plugin metadata.

    Examples:
        >>> get_plugin_metadata(plugin_path="./my-plugin")
        {
            'name': 'My Plugin',
            'code': 'my-plugin',
            'version': '1.0.0',
            'category': 'neural_net',
            'description': 'A custom ML plugin'
        }
    """
    if config is None:
        if plugin_path is None:
            raise ValueError('Either config or plugin_path must be provided')
        config = read_plugin_config(plugin_path)

    metadata_fields = ['name', 'code', 'version', 'category', 'description']
    metadata = {}

    for field in metadata_fields:
        if field in config:
            metadata[field] = config[field]

    return metadata
