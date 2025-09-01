from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod


@register_action
class PostAnnotationAction(Action):
    name = 'post_annotation'
    category = PluginCategory.POST_ANNOTATION
    method = RunMethod.TASK
