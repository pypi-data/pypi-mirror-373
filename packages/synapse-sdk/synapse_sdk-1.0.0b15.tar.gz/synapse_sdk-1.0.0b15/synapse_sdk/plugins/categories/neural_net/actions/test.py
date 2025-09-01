from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod


@register_action
class TestAction(Action):
    name = 'test'
    category = PluginCategory.NEURAL_NET
    method = RunMethod.JOB
