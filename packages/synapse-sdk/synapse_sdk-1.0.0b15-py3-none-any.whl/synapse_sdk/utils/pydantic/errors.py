from typing import Any, Dict

from synapse_sdk.utils.pydantic.config import ERROR_MESSAGES


def pydantic_to_drf_error(e):
    """
    Convert a pydantic ValidationError into a DRF-style error response.
    """
    drf_errors: Dict[str, Any] = {}

    for error in e.errors():
        field_path = error['loc']
        context_error = error.get('ctx', {}).get('error')

        error_msg = context_error or ERROR_MESSAGES.get(error['type'], error['msg'])

        # Convert the field path into a nested dictionary structure
        current = drf_errors
        for i, key in enumerate(field_path[:-1]):
            current = current.setdefault(str(key), {})

        # Set the error message at the final location
        final_key = str(field_path[-1])
        if final_key in current:
            if isinstance(current[final_key], list):
                current[final_key].append(error_msg)
            else:
                current[final_key] = [current[final_key], error_msg]
        else:
            current[final_key] = [error_msg]

    return drf_errors
