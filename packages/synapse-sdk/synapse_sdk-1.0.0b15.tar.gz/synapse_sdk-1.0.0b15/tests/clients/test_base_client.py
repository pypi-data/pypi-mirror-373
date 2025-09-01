import pytest
from pydantic import ValidationError

from synapse_sdk.clients.backend.models import Storage, UpdateJob
from synapse_sdk.clients.base import BaseClient


@pytest.fixture
def base_client():
    return BaseClient('http://fake_url')


@pytest.fixture
def valid_storage_response():
    return {
        'id': 1,
        'name': 'test_storage',
        'category': 'internal',
        'provider': 'file_system',
        'configuration': {},
        'is_default': True,
    }


@pytest.fixture
def invalid_storage_response(valid_storage_response):
    response = valid_storage_response.copy()
    response['provider'] = 'invalid_provider'
    return response


def test_validate_response_with_pydantic_model_success(base_client, valid_storage_response):
    validated_response = base_client._validate_response_with_pydantic_model(valid_storage_response, Storage)
    assert validated_response['id'] == valid_storage_response['id']


def test_validate_response_with_pydantic_model_invalid_data(base_client, invalid_storage_response):
    with pytest.raises(ValidationError) as exc_info:
        base_client._validate_response_with_pydantic_model(invalid_storage_response, Storage)
    assert '1 validation error' in str(exc_info.value)


def test_validate_response_with_pydantic_model_not_pydantic_model(base_client, valid_storage_response):
    with pytest.raises(TypeError) as exc_info:
        base_client._validate_response_with_pydantic_model(valid_storage_response, {})
    assert 'The provided model is not a pydantic model' in str(exc_info.value)


def test_validate_update_job_request_body_with_pydantic_model_success(base_client):
    request_body = {
        'status': 'running',
    }
    validated_request_body = base_client._validate_request_body_with_pydantic_model(
        request_body,
        UpdateJob,
    )
    assert validated_request_body['status'] == request_body['status']


def test_get_url_with_relative_path(base_client):
    """Test _get_url with relative path."""
    url = base_client._get_url('api/jobs')
    assert url == 'http://fake_url/api/jobs'


def test_get_url_with_leading_slash(base_client):
    """Test _get_url with leading slash in path."""
    url = base_client._get_url('/api/jobs')
    assert url == 'http://fake_url/api/jobs'


def test_get_url_with_full_url(base_client):
    """Test _get_url with full URL."""
    full_url = 'https://example.com/api/jobs'
    url = base_client._get_url(full_url)
    assert url == full_url


def test_get_url_with_trailing_slash_enabled(base_client):
    """Test _get_url with trailing_slash=True."""
    url = base_client._get_url('api/jobs', trailing_slash=True)
    assert url == 'http://fake_url/api/jobs/'


def test_get_url_with_trailing_slash_already_present(base_client):
    """Test _get_url with trailing_slash=True when slash already present."""
    url = base_client._get_url('api/jobs/', trailing_slash=True)
    assert url == 'http://fake_url/api/jobs/'


def test_get_url_with_trailing_slash_disabled(base_client):
    """Test _get_url with trailing_slash=False (default)."""
    url = base_client._get_url('api/jobs/')
    assert url == 'http://fake_url/api/jobs/'


def test_get_url_with_trailing_slash_full_url(base_client):
    """Test _get_url with trailing_slash=True and full URL."""
    full_url = 'https://example.com/api/jobs'
    url = base_client._get_url(full_url, trailing_slash=True)
    assert url == 'https://example.com/api/jobs/'


def test_get_url_with_http_protocol(base_client):
    """Test _get_url handles http:// URLs."""
    http_url = 'http://other.com/api'
    url = base_client._get_url(http_url)
    assert url == http_url


def test_get_url_with_https_protocol(base_client):
    """Test _get_url handles https:// URLs."""
    https_url = 'https://secure.com/api'
    url = base_client._get_url(https_url)
    assert url == https_url
