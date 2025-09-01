from enum import Enum


class RunMethod(Enum):
    """Plugin Execution Methods."""

    JOB = 'job'
    TASK = 'task'
    RESTAPI = 'restapi'


class PluginCategory(Enum):
    NEURAL_NET = 'neural_net'
    EXPORT = 'export'
    UPLOAD = 'upload'
    SMART_TOOL = 'smart_tool'
    POST_ANNOTATION = 'post_annotation'
    PRE_ANNOTATION = 'pre_annotation'
    DATA_VALIDATION = 'data_validation'

    @classmethod
    def choices(cls):
        return [(member.value, member.name.replace('_', ' ').title()) for member in cls]
