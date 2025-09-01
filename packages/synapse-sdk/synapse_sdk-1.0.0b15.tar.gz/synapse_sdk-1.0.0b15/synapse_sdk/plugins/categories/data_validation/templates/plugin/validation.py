from typing import Any, Dict, List, Optional

from synapse_sdk.plugins.categories.data_validation.actions.validation import ValidationDataStatus, ValidationResult


def validate(data: Optional[Dict[str, Any]] = None, **kwargs: Any) -> Dict[str, Any]:
    """Validate data with assignment data.

    * Custom validation logic can be added here.
    * Error messages can be added to the errors list if errors exist in data.
    * The validation result will be returned as a dict with ValidationResult structure.

    Args:
        data: The data to validate.
        **kwargs: Additional arguments.

    Returns:
        Dict[str, Any]: The validation result as a dictionary with ValidationResult structure.
    """
    errors: List[str] = []

    # Add custom validation logic here

    # Add error messages into errors list if errors exist in data

    # Determine status based on errors
    status = ValidationDataStatus.FAILED if errors else ValidationDataStatus.SUCCESS

    # DO NOT MODIFY BELOW THIS LINE - Validation result should be returned as a dumped ValidationResult.
    validation_result = ValidationResult(status=status, errors=errors)
    result_dict = validation_result.model_dump()
    result_dict['status'] = status.value
    return result_dict
