from unittest.mock import patch

import pytest

from synapse_sdk.plugins.categories.data_validation.actions.validation import (
    CriticalError,
    ValidationAction,
    ValidationDataStatus,
    ValidationParams,
    ValidationResult,
)


class TestValidationParams:
    """Test ValidationParams pydantic model."""

    def test_validation_params_creation(self):
        """Test creating ValidationParams instance."""
        params = ValidationParams(data={'test': 'data'})
        assert params.data == {'test': 'data'}

    def test_validation_params_model_validation(self):
        """Test ValidationParams model validation."""
        with pytest.raises(ValueError):
            ValidationParams(fake={'test': 'data'})  # Missing data


class TestValidationResult:
    """Test ValidationResult pydantic model."""

    def test_validation_result_creation_success(self):
        """Test creating ValidationResult instance with success status."""
        result = ValidationResult(status=ValidationDataStatus.SUCCESS, errors=[])
        assert result.status == ValidationDataStatus.SUCCESS
        assert result.errors == []

    def test_validation_result_creation_failed(self):
        """Test creating ValidationResult instance with failed status."""
        errors = ['Error 1', 'Error 2']
        result = ValidationResult(status=ValidationDataStatus.FAILED, errors=errors)
        assert result.status == ValidationDataStatus.FAILED
        assert result.errors == errors

    def test_validation_result_model_dump(self):
        """Test ValidationResult model_dump functionality."""
        result = ValidationResult(status=ValidationDataStatus.FAILED, errors=['Test error'])
        dumped = result.model_dump()
        assert dumped == {'status': 'failed', 'errors': ['Test error']}


@patch('synapse_sdk.plugins.utils.config.read_plugin_config', return_value={})
class TestValidationAction:
    """Test ValidationAction class."""

    def test_action_attributes(self, mock_config):
        """Test ValidationAction class attributes."""
        assert ValidationAction.name == 'validation'
        assert ValidationAction.category.value == 'data_validation'
        assert ValidationAction.method.value == 'task'
        assert ValidationAction.params_model == ValidationParams


class TestCriticalError:
    """Test CriticalError exception class."""

    def test_critical_error_default_message(self):
        """Test CriticalError with default message."""
        error = CriticalError()
        assert str(error) == 'Critical error occured while processing validation'
        assert error.message == 'Critical error occured while processing validation'

    def test_critical_error_custom_message(self):
        """Test CriticalError with custom message."""
        custom_message = 'Custom validation error'
        error = CriticalError(custom_message)
        assert str(error) == custom_message
        assert error.message == custom_message


class TestValidationDataStatus:
    """Test ValidationDataStatus enum."""

    def test_validation_data_status_values(self):
        """Test ValidationDataStatus enum values."""
        assert ValidationDataStatus.SUCCESS == 'success'
        assert ValidationDataStatus.FAILED == 'failed'

    def test_validation_data_status_string_conversion(self):
        """Test ValidationDataStatus string conversion."""
        assert ValidationDataStatus.SUCCESS.value == 'success'
        assert ValidationDataStatus.FAILED.value == 'failed'
