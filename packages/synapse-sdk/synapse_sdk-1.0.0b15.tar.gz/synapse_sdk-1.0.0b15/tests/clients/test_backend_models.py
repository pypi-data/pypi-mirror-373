import pytest
from pydantic import ValidationError

from synapse_sdk.clients.backend.models import JobStatus, Storage, StorageCategory, StorageProvider, UpdateJob


def test_storage_model_validation_success():
    storage_response = {
        'id': 1,
        'name': 'test_storage',
        'category': 'internal',
        'provider': 'file_system',
        'configuration': {},
        'is_default': True,
    }
    storage = Storage(**storage_response)
    assert storage.id == 1


def test_storage_model_validation_failed_with_invalid_category():
    storage_response = {
        'id': 1,
        'name': 'test_storage',
        'category': 'invalid_data',
        'provider': 'file_system',
        'configuration': {},
        'is_default': True,
    }
    with pytest.raises(ValidationError) as exc_info:
        Storage(**storage_response)
    assert 'category' in str(exc_info.value)


def test_storage_model_validation_failed_with_invalid_provider():
    storage_response = {
        'id': 1,
        'name': 'test_storage',
        'category': 'internal',
        'provider': 'invalid_provider',
        'configuration': {},
        'is_default': True,
    }
    with pytest.raises(ValidationError) as exc_info:
        Storage(**storage_response)
    assert 'provider' in str(exc_info.value)


def test_storage_model_validation_failed_with_missing_field():
    storage_response = {
        'id': 1,
        'name': 'test_storage',
        'category': 'internal',
        'provider': 'file_system',
        'is_default': True,
        # Missing configuration field
    }
    with pytest.raises(ValidationError):
        Storage(**storage_response)


def test_storage_model_enum_values():
    # Test that valid enum values work correctly
    for category in StorageCategory:
        for provider in StorageProvider:
            storage = Storage(
                id=1,
                name='test_storage',
                category=category,
                provider=provider,
                configuration={},
                is_default=True,
            )
            assert storage.category == category
            assert storage.provider == provider


def test_update_job_model_validation_success():
    job_response = {
        'status': JobStatus.RUNNING,
        'progress_record': {'key': 'value'},
        'console_logs': {'log': 'log content'},
        'result': {'result_key': 'result_value'},
    }
    update_job = UpdateJob(**job_response)
    assert update_job.status == JobStatus.RUNNING
    assert update_job.progress_record == {'key': 'value'}
    assert update_job.console_logs == {'log': 'log content'}
    assert update_job.result == {'result_key': 'result_value'}


def test_update_job_model_validation_with_single_field_success():
    job_response = {
        'status': JobStatus.RUNNING,
    }
    update_job = UpdateJob(**job_response)
    assert update_job.status == JobStatus.RUNNING
    assert update_job.progress_record is None
    assert update_job.console_logs is None
    assert update_job.result is None


def test_update_job_model_validation_with_console_logs_as_list():
    job_response = {
        'status': JobStatus.RUNNING,
        'console_logs': ['log line 1', 'log line 2', 'log line 3'],
    }
    update_job = UpdateJob(**job_response)
    assert update_job.status == JobStatus.RUNNING
    assert update_job.console_logs == ['log line 1', 'log line 2', 'log line 3']
    assert update_job.progress_record is None
    assert update_job.result is None


def test_update_job_model_validation_with_result_as_list():
    job_response = {
        'status': JobStatus.RUNNING,
        'result': ['result item 1', 'result item 2', 'result item 3'],
    }
    update_job = UpdateJob(**job_response)
    assert update_job.status == JobStatus.RUNNING
    assert update_job.result == ['result item 1', 'result item 2', 'result item 3']
    assert update_job.progress_record is None
    assert update_job.console_logs is None


def test_update_job_model_validation_with_metrics_record():
    job_response = {
        'status': JobStatus.RUNNING,
        'metrics_record': {'metric_key': 'metric_value'},
    }
    update_job = UpdateJob(**job_response)
    assert update_job.status == JobStatus.RUNNING
    assert update_job.metrics_record == {'metric_key': 'metric_value'}
    assert update_job.progress_record is None
    assert update_job.console_logs is None
    assert update_job.result is None


def test_update_job_model_validation_with_all_fields():
    job_response = {
        'status': JobStatus.RUNNING,
        'progress_record': {'progress_key': 'progress_value'},
        'metrics_record': {'metrics_key': 'metrics_value'},
        'console_logs': {'log_key': 'log_value'},
        'result': {'result_key': 'result_value'},
    }
    update_job = UpdateJob(**job_response)
    assert update_job.status == JobStatus.RUNNING
    assert update_job.progress_record == {'progress_key': 'progress_value'}
    assert update_job.metrics_record == {'metrics_key': 'metrics_value'}
    assert update_job.console_logs == {'log_key': 'log_value'}
    assert update_job.result == {'result_key': 'result_value'}


def test_update_job_model_validation_with_metrics_record_as_empty_dict():
    job_response = {
        'status': JobStatus.RUNNING,
        'metrics_record': {},
    }
    update_job = UpdateJob(**job_response)
    assert update_job.status == JobStatus.RUNNING
    assert update_job.metrics_record == {}
    assert update_job.progress_record is None
    assert update_job.console_logs is None
    assert update_job.result is None


def test_update_job_model_validation_with_metrics_record_and_console_logs():
    job_response = {
        'status': JobStatus.RUNNING,
        'metrics_record': {'accuracy': 0.95, 'loss': 0.1},
        'console_logs': ['log line 1', 'log line 2'],
    }
    update_job = UpdateJob(**job_response)
    assert update_job.status == JobStatus.RUNNING
    assert update_job.metrics_record == {'accuracy': 0.95, 'loss': 0.1}
    assert update_job.console_logs == ['log line 1', 'log line 2']
    assert update_job.progress_record is None
    assert update_job.result is None
