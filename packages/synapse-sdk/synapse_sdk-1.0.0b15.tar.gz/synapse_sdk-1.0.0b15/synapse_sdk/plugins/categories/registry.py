import pkgutil
from importlib import import_module

from synapse_sdk.plugins.enums import PluginCategory

_REGISTERED_ACTIONS = {}


def register_actions():
    if not _REGISTERED_ACTIONS:
        for category in PluginCategory:
            plugin_category_module_name = f'synapse_sdk.plugins.categories.{category.value}.actions'
            plugin_category_module = import_module(plugin_category_module_name)
            for _, action_name, _ in pkgutil.iter_modules(plugin_category_module.__path__):
                action_module_name = f'{plugin_category_module_name}.{action_name}'
                import_module(action_module_name)
