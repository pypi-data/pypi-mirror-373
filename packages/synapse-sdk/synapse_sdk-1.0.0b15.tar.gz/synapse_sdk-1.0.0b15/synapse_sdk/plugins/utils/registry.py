"""Plugin registry utilities."""

from typing import List

from synapse_sdk.plugins.enums import PluginCategory


def get_plugin_categories() -> List[str]:
    """Get list of all available plugin categories.

    Returns:
        List of plugin category names.

    Examples:
        >>> get_plugin_categories()
        ['neural_net', 'export', 'upload', 'smart_tool', 'post_annotation', 'pre_annotation', 'data_validation']
    """
    return [plugin_category.value for plugin_category in PluginCategory]


def is_valid_category(category: str) -> bool:
    """Check if a category is valid.

    Args:
        category: Category name to validate.

    Returns:
        True if category is valid, False otherwise.

    Examples:
        >>> is_valid_category('neural_net')
        True
        >>> is_valid_category('invalid_category')
        False
    """
    return category in get_plugin_categories()


def get_category_display_name(category: str) -> str:
    """Get human-readable display name for a category.

    Args:
        category: Category name.

    Returns:
        Human-readable category name.

    Examples:
        >>> get_category_display_name('neural_net')
        'Neural Net'
        >>> get_category_display_name('data_validation')
        'Data Validation'
    """
    try:
        plugin_category = PluginCategory(category)
        return plugin_category.name.replace('_', ' ').title()
    except ValueError:
        return category.replace('_', ' ').title()
