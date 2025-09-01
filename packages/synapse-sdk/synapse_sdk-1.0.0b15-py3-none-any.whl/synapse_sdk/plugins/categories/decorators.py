from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.registry import _REGISTERED_ACTIONS


def register_action(action_class):
    if not issubclass(action_class, Action):
        raise ValueError('Wrapped class must subclass Action class.')

    try:
        _REGISTERED_ACTIONS[action_class.category.value][action_class.name] = action_class
    except KeyError:
        _REGISTERED_ACTIONS[action_class.category.value] = {action_class.name: action_class}
    return action_class
