from enum import Enum
from typing import Any, Dict, List

from pydantic import BaseModel

from synapse_sdk.plugins.categories.base import Action
from synapse_sdk.plugins.categories.decorators import register_action
from synapse_sdk.plugins.enums import PluginCategory, RunMethod


class ValidationDataStatus(str, Enum):
    """Validation data status enumeration.

    Represents the possible status values for validation operations.

    Attributes:
        SUCCESS: Validation completed successfully with no errors.
        FAILED: Validation failed with one or more errors.
    """

    SUCCESS = 'success'
    FAILED = 'failed'


class ValidationResult(BaseModel):
    """Validation result model.

    Args:
        status: The validation status.
        errors: List of validation errors.
    """

    status: ValidationDataStatus
    errors: List[str]


class CriticalError(Exception):
    """Critical error exception for validation processing.

    Raised when a critical error occurs during validation that prevents
    the validation process from continuing normally.

    Args:
        message: Custom error message. Defaults to a standard critical error message.

    Attributes:
        message: The error message associated with this exception.
    """

    def __init__(self, message: str = 'Critical error occured while processing validation'):
        self.message = message
        super().__init__(self.message)


class ValidationParams(BaseModel):
    """Validation action parameters.

    Args:
        data (dict): The validation data.
    """

    data: Dict[str, Any]


@register_action
class ValidationAction(Action):
    """Validation action for data validation processing.

    This action handles the process of validating data with assignment IDs.
    It supports validation methods and provides structured logging.

    Attrs:
        name (str): Action name, set to 'validation'.
        category (PluginCategory): Plugin category, set to DATA_VALIDATION.
        method (RunMethod): Execution method, set to TASK.
        params_model (Type[ValidationParams]): Parameter validation model.
    """

    name = 'validation'
    category = PluginCategory.DATA_VALIDATION
    method = RunMethod.TASK
    params_model = ValidationParams
