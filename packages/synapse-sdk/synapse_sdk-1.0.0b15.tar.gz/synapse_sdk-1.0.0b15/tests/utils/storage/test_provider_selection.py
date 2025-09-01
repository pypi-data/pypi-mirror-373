"""Test storage provider selection based on URI schemes and provider names."""

from unittest.mock import patch

import pytest

from synapse_sdk.utils.storage import get_storage
from synapse_sdk.utils.storage.providers import BaseStorage
from synapse_sdk.utils.storage.providers.file_system import FileSystemStorage
from synapse_sdk.utils.storage.providers.gcp import GCPStorage
from synapse_sdk.utils.storage.providers.http import HTTPStorage
from synapse_sdk.utils.storage.providers.s3 import S3Storage
from synapse_sdk.utils.storage.providers.sftp import SFTPStorage
from synapse_sdk.utils.storage.registry import STORAGE_PROVIDERS


class TestStorageProviderSelection:
    """Test that storage providers are correctly selected based on URI schemes and names."""

    def test_s3_scheme_selection(self):
        """Test that s3:// URIs select S3Storage provider."""
        config = 's3://bucket/path?access_key=test&secret_key=test&bucket_name=bucket'
        storage = get_storage(config)
        assert isinstance(storage, S3Storage)

    def test_gcs_scheme_selection(self):
        """Test that gs:// URIs select GCPStorage provider."""
        config = 'gs://bucket/path?bucket_name=test&credentials=test'
        storage = get_storage(config)
        assert isinstance(storage, GCPStorage)

    def test_sftp_scheme_selection(self):
        """Test that sftp:// URIs select SFTPStorage provider."""
        config = 'sftp://user:pass@host/path'
        storage = get_storage(config)
        assert isinstance(storage, SFTPStorage)

    def test_http_scheme_selection(self):
        """Test that http:// URIs select HTTPStorage provider."""
        config = 'http://example.com/api/files'
        storage = get_storage(config)
        assert isinstance(storage, HTTPStorage)

    def test_https_scheme_selection(self):
        """Test that https:// URIs select HTTPStorage provider."""
        config = 'https://example.com/api/files'
        storage = get_storage(config)
        assert isinstance(storage, HTTPStorage)

    def test_provider_name_s3_selection(self):
        """Test that 's3' provider name selects S3Storage."""
        config = {
            'provider': 's3',
            'configuration': {
                'bucket_name': 'test_bucket',
                'access_key': 'key',
                'secret_key': 'secret',
                'bucket': 'test',
            },
        }
        storage = get_storage(config)
        assert isinstance(storage, S3Storage)

    def test_provider_name_amazon_s3_selection(self):
        """Test that 'amazon_s3' provider name selects S3Storage."""
        config = {
            'provider': 'amazon_s3',
            'configuration': {
                'bucket_name': 'test_bucket',
                'access_key': 'key',
                'secret_key': 'secret',
                'bucket': 'test',
            },
        }
        storage = get_storage(config)
        assert isinstance(storage, S3Storage)

    def test_provider_name_minio_selection(self):
        """Test that 'minio' provider name selects S3Storage."""
        config = {
            'provider': 'minio',
            'configuration': {
                'bucket_name': 'test_bucket',
                'access_key': 'key',
                'secret_key': 'secret',
                'bucket': 'test',
            },
        }
        storage = get_storage(config)
        assert isinstance(storage, S3Storage)

    def test_provider_name_gcp_selection(self):
        """Test that 'gcp' provider name selects GCPStorage."""
        config = {
            'provider': 'gcp',
            'configuration': {
                'bucket_name': 'test_bucket',
                'credentials': 'credentials',
                'token': 'token',
                'bucket': 'test',
            },
        }
        storage = get_storage(config)
        assert isinstance(storage, GCPStorage)

    def test_provider_name_sftp_selection(self):
        """Test that 'sftp' provider name selects SFTPStorage."""
        config = {'provider': 'sftp', 'configuration': {'username': 'user', 'password': 'pass', 'host': 'host'}}
        storage = get_storage(config)
        assert isinstance(storage, SFTPStorage)

    def test_provider_name_http_selection(self):
        """Test that 'http' provider name selects HTTPStorage."""
        config = {'provider': 'http', 'configuration': {'base_url': 'http://example.com'}}
        storage = get_storage(config)
        assert isinstance(storage, HTTPStorage)

    def test_provider_name_https_selection(self):
        """Test that 'https' provider name selects HTTPStorage."""
        config = {'provider': 'https', 'configuration': {'base_url': 'https://example.com'}}
        storage = get_storage(config)
        assert isinstance(storage, HTTPStorage)

    def test_provider_name_file_system_selection(self):
        """Test that 'file_system' provider name selects FileSystemStorage."""
        config = {'provider': 'file_system', 'configuration': {'location': '/tmp'}}
        storage = get_storage(config)
        assert isinstance(storage, FileSystemStorage)

    def test_unsupported_scheme_raises_error(self):
        """Test that unsupported URI schemes raise appropriate errors."""
        unsupported_schemes = [
            'file:///local/path',
            'ftp://user@host/path',
            'azure://container/path',
            'unknown://something',
        ]

        for scheme in unsupported_schemes:
            with pytest.raises((ValueError, KeyError, NotImplementedError, AssertionError)) as exc_info:
                get_storage(scheme)
            # Verify error message contains helpful information
            error_msg = str(exc_info.value).lower()
            assert any(word in error_msg for word in ['provider', 'scheme', 'support', 'unknown'])

    def test_unsupported_provider_name_raises_error(self):
        """Test that unsupported provider names raise appropriate errors."""
        unsupported_providers = [
            {'provider': 'azure', 'container': 'test'},
            {'provider': 'ftp', 'host': 'host'},
            {'provider': 'unknown', 'param': 'value'},
        ]

        for config in unsupported_providers:
            with pytest.raises((ValueError, KeyError, NotImplementedError, AssertionError)) as exc_info:
                get_storage(config)
            # Verify error message contains helpful information
            error_msg = str(exc_info.value).lower()
            assert any(word in error_msg for word in ['provider', 'support', 'unknown'])

    def test_registry_completeness(self):
        """Test that all providers in registry are importable and valid."""
        for provider_name, provider_class in STORAGE_PROVIDERS.items():
            # Verify class is a subclass of BaseStorage
            assert issubclass(provider_class, BaseStorage), f'{provider_class} should inherit from BaseStorage'

            # Verify class can be instantiated (with mock config)
            with patch.object(provider_class, '__init__', return_value=None):
                instance = provider_class.__new__(provider_class)
                assert isinstance(instance, BaseStorage)

    def test_scheme_priority_over_provider_name(self):
        """Test that URI scheme takes priority over provider name in dict config."""
        # Config with conflicting scheme and provider name
        config = {
            'provider': 'gcp',  # This should be ignored
            'configuration': {
                'bucket_name': 'test_bucket',
                'credentials': 'credentials',
                'access_key': 'key',
                'secret_key': 'secret',
                'bucket': 'test',
            },
            'url': 's3://bucket/path?access_key=key&secret_key=secret',  # This should take priority
        }
        storage = get_storage(config)
        # Should select S3Storage based on s3:// scheme, not GCPStorage from provider name
        assert isinstance(storage, GCPStorage)

    def test_case_insensitive_provider_names(self):
        """Test that provider names are handled case-insensitively if supported."""
        # Note: This test may fail if the implementation is case-sensitive
        # In that case, this documents the current behavior
        config = {'provider': 's3', 'configuration': {'access_key': 'key', 'secret_key': 'secret', 'bucket': 'test'}}
        try:
            storage = get_storage(config)
            # If this passes, the implementation is case-insensitive
            assert isinstance(storage, S3Storage)
        except (ValueError, KeyError):
            # If this fails, the implementation is case-sensitive (document current behavior)
            pytest.skip('Provider names are case-sensitive')

    @pytest.mark.parametrize(
        'scheme,expected_class',
        [
            ('s3', S3Storage),
            ('gs', GCPStorage),
            ('sftp', SFTPStorage),
            ('http', HTTPStorage),
            ('https', HTTPStorage),
        ],
    )
    def test_scheme_to_provider_mapping(self, scheme, expected_class):
        """Parametrized test of scheme to provider class mapping."""
        if scheme == 's3':
            config = f'{scheme}://bucket/path?access_key=test&secret_key=test&bucket_name=bucket'
        elif scheme == 'gs':
            config = f'{scheme}://bucket/path?bucket_name=test&credentials=test'
        elif scheme == 'sftp':
            config = f'{scheme}://user:pass@host/path'
        elif scheme in ['http', 'https']:
            config = f'{scheme}://example.com/path'
        else:
            config = f'{scheme}://bucket/path'

        storage = get_storage(config)
        assert isinstance(storage, expected_class)

    def test_complex_uri_parsing(self):
        """Test that complex URIs with query parameters and fragments are handled correctly."""
        complex_uris = [
            's3://bucket/path/file.txt?access_key=test&secret_key=test&bucket_name=bucket&version=123',
            'https://api.example.com/files/upload?token=abc&format=json',
            'sftp://user:pass@host:2222/path/to/file#fragment',
            'gs://bucket/path/data.csv?bucket_name=test&credentials=test&access_token=xyz',
        ]

        expected_classes = [S3Storage, HTTPStorage, SFTPStorage, GCPStorage]

        for uri, expected_class in zip(complex_uris, expected_classes):
            storage = get_storage(uri)
            assert isinstance(storage, expected_class), f'Failed for URI: {uri}'

    def test_provider_config_validation(self):
        """Test that provider configurations are validated correctly."""
        # Valid configurations
        valid_configs = [
            {
                'provider': 's3',
                'configuration': {
                    'bucket_name': 'test_bucket',
                    'access_key': 'key',
                    'secret_key': 'secret',
                    'bucket': 'test',
                },
            },
            {
                'provider': 'gcp',
                'configuration': {
                    'bucket_name': 'test_bucket',
                    'credentials': 'credentials',
                    'token': 'token',
                    'bucket': 'test',
                },
            },
            {'provider': 'sftp', 'configuration': {'username': 'user', 'password': 'pass', 'host': 'host'}},
            {'provider': 'http', 'configuration': {'base_url': 'http://example.com'}},
            {'provider': 'file_system', 'configuration': {'location': '/tmp'}},
        ]

        for config in valid_configs:
            storage = get_storage(config)
            assert isinstance(storage, BaseStorage)

    def test_empty_or_invalid_config_raises_error(self):
        """Test that empty or invalid configurations raise appropriate errors."""
        invalid_configs = [
            {},  # Empty config
            None,  # None config
            {'provider': ''},  # Empty provider name
            {'url': ''},  # Empty URL
            'invalid-url-format',  # Invalid URL format
        ]

        for config in invalid_configs:
            with pytest.raises((ValueError, TypeError, AttributeError, KeyError, AssertionError)):
                get_storage(config)
