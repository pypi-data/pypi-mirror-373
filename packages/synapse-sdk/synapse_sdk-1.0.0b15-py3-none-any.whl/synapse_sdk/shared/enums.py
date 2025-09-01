from enum import Enum


class Context(str, Enum):
    """Context levels for logging and message categorization.

    This enum defines different context levels that can be used for logging messages,
    UI feedback, and other categorization purposes throughout the application.

    Usage:
        # In logging methods
        self.log_message("Operation completed", context=Context.SUCCESS.value)
        self.log_message("Warning: deprecated method", context=Context.WARNING.value)

        # In LOG_MESSAGES dictionary
        LOG_MESSAGES = {
            'SUCCESS_CODE': {'message': 'Success!', 'level': Context.SUCCESS},
            'ERROR_CODE': {'message': 'Error occurred', 'level': Context.DANGER},
        }

        # In UI components for styling/theming
        if context == Context.DANGER:
            render_error_style()
        elif context == Context.SUCCESS:
            render_success_style()

    Attributes:
        INFO: General informational messages (neutral)
        SUCCESS: Success messages and positive outcomes
        WARNING: Warning messages for non-critical issues
        DANGER: Error messages and critical failures
        ERROR: Legacy error context (use DANGER for new implementations)
        DEBUG: Debug-level messages for development
    """

    INFO = 'info'
    SUCCESS = 'success'
    WARNING = 'warning'
    DANGER = 'danger'
    ERROR = 'error'
    DEBUG = 'debug'


class SupportedTools(Enum):
    """Enum for supported annotation tools.

    * TODO: Need dynamic configuration by referencing apps/annotation/categories/{file_type}/settings.py.
        * Currently difficult to configure due to non-standardized prompt file types.
    """

    BOUNDING_BOX = 'bounding_box', 'bounding_box'
    NAMED_ENTITY = 'named_entity', 'named_entity'
    CLASSIFICATION = 'classification', 'classification'
    POLYLINE = 'polyline', 'polyline'
    KEYPOINT = 'keypoint', 'keypoint'
    BOUNDING_BOX_3D = '3d_bounding_box', '3d_bounding_box'
    IMAGE_SEGMENTATION = 'segmentation', 'image_segmentation'
    VIDEO_SEGMENTATION = 'segmentation', 'video_segmentation'
    SEGMENTATION_3D = '3d_segmentation', '3d_segmentation'
    POLYGON = 'polygon', 'polygon'
    RELATION = 'relation', 'relation'
    GROUP = 'group', 'group'
    PROMPT = 'prompt', 'prompt'
    ANSWER = 'answer', 'answer'

    def __init__(self, annotation_tool, method_name):
        self.annotation_tool = annotation_tool
        self.method_name = method_name

    @classmethod
    def get_all_values(cls):
        """Get all tool values as a list."""
        return [tool.value for tool in cls]

    @classmethod
    def get_tools_for_file_type(cls, file_type):
        """Get tools supported for a specific file type."""
        basic_tools = [cls.RELATION, cls.GROUP, cls.CLASSIFICATION]

        if file_type == 'image':
            basic_tools.extend([
                cls.BOUNDING_BOX,
                cls.POLYLINE,
                cls.KEYPOINT,
                cls.IMAGE_SEGMENTATION,
                cls.POLYGON,
            ])
        elif file_type == 'video':
            basic_tools.extend([
                cls.BOUNDING_BOX,
                cls.POLYLINE,
                cls.KEYPOINT,
                cls.VIDEO_SEGMENTATION,
                cls.POLYGON,
            ])
        elif file_type == 'pcd':
            basic_tools.extend([cls.BOUNDING_BOX_3D, cls.SEGMENTATION_3D])
        elif file_type == 'text':
            basic_tools.extend([cls.PROMPT, cls.ANSWER, cls.NAMED_ENTITY])

        return basic_tools
