"""Plugin action utilities."""

import json
from typing import Any, Dict, Union

from synapse_sdk.plugins.categories.registry import _REGISTERED_ACTIONS, register_actions
from synapse_sdk.utils.file import get_dict_from_file

from .config import read_plugin_config


def get_action(action: str, params_data: Union[str, Dict[str, Any]], *args, **kwargs):
    """Get a plugin action instance with validated parameters.

    Args:
        action: Name of the action to get.
        params_data: Parameters as string (JSON/file path) or dictionary.
        *args: Additional positional arguments.
        **kwargs: Additional keyword arguments including 'config'.

    Returns:
        Configured action instance ready for execution.

    Raises:
        ActionError: If parameters are invalid or action not found.
    """
    if isinstance(params_data, str):
        try:
            params = json.loads(params_data)
        except json.JSONDecodeError:
            params = get_dict_from_file(params_data)
    else:
        params = params_data

    config_data = kwargs.pop('config', False)
    if config_data:
        if isinstance(config_data, str):
            config = read_plugin_config(plugin_path=config_data)
        else:
            config = config_data
    else:
        config = read_plugin_config()

    category = config['category']
    return get_action_class(category, action)(params, config, *args, **kwargs)


def get_action_class(category: str, action: str):
    """Get action class by category and action name.

    Args:
        category: Plugin category (e.g., 'neural_net', 'export').
        action: Action name (e.g., 'train', 'inference').

    Returns:
        Action class ready for instantiation.

    Raises:
        KeyError: If category or action not found in registry.
    """
    register_actions()
    try:
        return _REGISTERED_ACTIONS[category][action]
    except KeyError as e:
        if category not in _REGISTERED_ACTIONS:
            available_categories = list(_REGISTERED_ACTIONS.keys())
            raise KeyError(f"Category '{category}' not found. Available categories: {available_categories}") from e
        else:
            available_actions = list(_REGISTERED_ACTIONS[category].keys())
            raise KeyError(
                f"Action '{action}' not found in category '{category}'. Available actions: {available_actions}"
            ) from e


def get_available_actions(category: str) -> list:
    """Get list of available actions for a plugin category.

    Args:
        category: Plugin category to get actions for.

    Returns:
        List of available action names.

    Raises:
        KeyError: If category not found in registry.

    Examples:
        >>> get_available_actions('neural_net')
        ['train', 'inference', 'test', 'deployment', 'gradio', 'tune']
    """
    register_actions()
    if category not in _REGISTERED_ACTIONS:
        available_categories = list(_REGISTERED_ACTIONS.keys())
        raise KeyError(f"Category '{category}' not found. Available categories: {available_categories}")

    return list(_REGISTERED_ACTIONS[category].keys())


def is_action_available(category: str, action: str) -> bool:
    """Check if an action is available in a given category.

    Args:
        category: Plugin category to check.
        action: Action name to check.

    Returns:
        True if action is available, False otherwise.

    Examples:
        >>> is_action_available('neural_net', 'train')
        True
        >>> is_action_available('neural_net', 'nonexistent')
        False
    """
    try:
        available_actions = get_available_actions(category)
        return action in available_actions
    except KeyError:
        return False
