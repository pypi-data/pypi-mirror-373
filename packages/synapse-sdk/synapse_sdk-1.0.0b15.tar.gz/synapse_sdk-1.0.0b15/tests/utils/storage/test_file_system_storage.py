"""Test cases for FileSystemStorage provider."""

import os
import tempfile
from pathlib import Path

import pytest

from synapse_sdk.utils.storage.providers.file_system import FileSystemStorage


class TestFileSystemStorage:
    """Test cases for FileSystemStorage provider."""

    @pytest.fixture
    def temp_dir(self):
        """Create a temporary directory for testing."""
        with tempfile.TemporaryDirectory() as temp_dir:
            yield Path(temp_dir)

    @pytest.fixture
    def temp_file(self, temp_dir):
        """Create a temporary file for testing."""
        test_file = temp_dir / 'test_source.txt'
        test_file.write_text('test content for upload')
        return test_file

    @pytest.fixture
    def sample_files(self, temp_dir):
        """Create sample files and directories for testing."""
        # Create directory structure
        (temp_dir / 'subdir1').mkdir()
        (temp_dir / 'subdir2').mkdir()
        (temp_dir / 'subdir1' / 'nested').mkdir()

        # Create files with different sizes
        (temp_dir / 'file1.txt').write_text('content1')  # 8 bytes
        (temp_dir / 'file2.txt').write_text('content22')  # 9 bytes
        (temp_dir / 'subdir1' / 'file3.txt').write_text('content333')  # 10 bytes
        (temp_dir / 'subdir1' / 'nested' / 'file4.txt').write_text('content4444')  # 11 bytes
        (temp_dir / 'subdir2' / 'file5.txt').write_text('content55555')  # 12 bytes

        return temp_dir

    def test_init_with_dict_config(self, temp_dir):
        """Test initialization with dict-based configuration."""
        config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir)}}
        storage = FileSystemStorage(config)
        assert storage.base_path == temp_dir

    def test_init_with_relative_path(self, temp_dir):
        """Test initialization with relative path."""
        # Create a subdirectory
        subdir = temp_dir / 'data'
        subdir.mkdir()

        config = {'provider': 'file_system', 'configuration': {'location': str(subdir)}}
        storage = FileSystemStorage(config)
        assert storage.base_path == subdir

    def test_init_missing_base_path_raises_error(self):
        """Test that missing base_path raises KeyError."""
        config = {'provider': 'file_system', 'configuration': {}}
        with pytest.raises(KeyError):
            FileSystemStorage(config)

    def test_upload_success(self, temp_dir, temp_file):
        """Test successful file upload."""
        config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir)}}
        storage = FileSystemStorage(config)
        target = 'uploaded_file.txt'

        result_url = storage.upload(str(temp_file), target)

        # Check file was copied
        target_path = temp_dir / target
        assert target_path.exists()
        assert target_path.read_text() == 'test content for upload'

        # Check return URL
        expected_url = f'file://{target_path.absolute()}'
        assert result_url == expected_url

    def test_upload_creates_directories(self, temp_dir, temp_file):
        """Test upload creates parent directories if they don't exist."""
        config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir)}}
        storage = FileSystemStorage(config)
        target = 'nested/deep/uploaded_file.txt'

        storage.upload(str(temp_file), target)

        # Check directories were created
        target_path = temp_dir / target
        assert target_path.exists()
        assert target_path.parent.exists()
        assert target_path.read_text() == 'test content for upload'

    def test_upload_to_subdirectory(self, temp_dir, temp_file):
        """Test upload to existing subdirectory."""
        subdir = temp_dir / 'existing_subdir'
        subdir.mkdir()

        config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir)}}
        storage = FileSystemStorage(config)
        target = 'existing_subdir/uploaded_file.txt'

        storage.upload(str(temp_file), target)

        target_path = temp_dir / target
        assert target_path.exists()
        assert target_path.read_text() == 'test content for upload'

    def test_exists_true_for_existing_file(self, sample_files):
        """Test exists returns True for existing file."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)
        assert storage.exists('file1.txt') is True
        assert storage.exists('subdir1/file3.txt') is True

    def test_exists_false_for_nonexistent_file(self, sample_files):
        """Test exists returns False for non-existent file."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)
        assert storage.exists('nonexistent.txt') is False
        assert storage.exists('subdir1/nonexistent.txt') is False

    def test_exists_true_for_directory(self, sample_files):
        """Test exists returns True for directories."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)
        assert storage.exists('subdir1') is True

    def test_get_url_returns_file_url(self, sample_files):
        """Test get_url returns correct file:// URL."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)
        target = 'file1.txt'

        result_url = storage.get_url(target)

        expected_path = sample_files / target
        expected_url = f'file://{expected_path.absolute()}'
        assert result_url == expected_url

    def test_get_url_for_nested_file(self, sample_files):
        """Test get_url for nested file."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)
        target = 'subdir1/nested/file4.txt'

        result_url = storage.get_url(target)

        expected_path = sample_files / target
        expected_url = f'file://{expected_path.absolute()}'
        assert result_url == expected_url

    def test_get_pathlib_returns_path_object(self, sample_files):
        """Test get_pathlib returns Path object."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)
        target = 'file1.txt'

        result_path = storage.get_pathlib(target)

        expected_path = sample_files / target
        assert result_path == expected_path
        assert isinstance(result_path, Path)

    def test_get_pathlib_for_nested_path(self, sample_files):
        """Test get_pathlib for nested path."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)
        target = 'subdir1/nested/file4.txt'

        result_path = storage.get_pathlib(target)

        expected_path = sample_files / target
        assert result_path == expected_path

    def test_get_pathlib_with_root_slash(self, sample_files):
        """Test get_pathlib with '/' returns base path."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)

        result_path = storage.get_pathlib('/')

        assert result_path == sample_files
        assert isinstance(result_path, Path)

    def test_get_pathlib_with_empty_string(self, sample_files):
        """Test get_pathlib with empty string returns base path."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)

        result_path = storage.get_pathlib('')

        assert result_path == sample_files
        assert isinstance(result_path, Path)

    def test_get_path_file_count_single_file(self, sample_files):
        """Test get_path_file_count for single file."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)
        file_path = storage.get_pathlib('file1.txt')

        count = storage.get_path_file_count(file_path)

        assert count == 1

    def test_get_path_file_count_directory(self, sample_files):
        """Test get_path_file_count for directory."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)

        # Root directory should have 5 files total
        root_path = storage.get_pathlib('')
        count = storage.get_path_file_count(root_path)
        assert count == 5

        # subdir1 should have 2 files (file3.txt and nested/file4.txt)
        subdir1_path = storage.get_pathlib('subdir1')
        count = storage.get_path_file_count(subdir1_path)
        assert count == 2

        # subdir2 should have 1 file
        subdir2_path = storage.get_pathlib('subdir2')
        count = storage.get_path_file_count(subdir2_path)
        assert count == 1

    def test_get_path_file_count_nonexistent_path(self, sample_files):
        """Test get_path_file_count for non-existent path."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)
        nonexistent_path = storage.get_pathlib('nonexistent')

        count = storage.get_path_file_count(nonexistent_path)

        assert count == 0

    def test_get_path_total_size_single_file(self, sample_files):
        """Test get_path_total_size for single file."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)
        file_path = storage.get_pathlib('file1.txt')  # "content1" = 8 bytes

        size = storage.get_path_total_size(file_path)

        assert size == 8

    def test_get_path_total_size_directory(self, sample_files):
        """Test get_path_total_size for directory."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)

        # Calculate expected total size: 8 + 9 + 10 + 11 + 12 = 50 bytes
        root_path = storage.get_pathlib('')
        total_size = storage.get_path_total_size(root_path)
        assert total_size == 50

        # subdir1 should have: 10 + 11 = 21 bytes
        subdir1_path = storage.get_pathlib('subdir1')
        size = storage.get_path_total_size(subdir1_path)
        assert size == 21

        # subdir2 should have: 12 bytes
        subdir2_path = storage.get_pathlib('subdir2')
        size = storage.get_path_total_size(subdir2_path)
        assert size == 12

    def test_get_path_total_size_nonexistent_path(self, sample_files):
        """Test get_path_total_size for non-existent path."""
        config = {'provider': 'file_system', 'configuration': {'location': str(sample_files)}}
        storage = FileSystemStorage(config)
        nonexistent_path = storage.get_pathlib('nonexistent')

        size = storage.get_path_total_size(nonexistent_path)

        assert size == 0

    def test_upload_overwrites_existing_file(self, temp_dir, temp_file):
        """Test upload overwrites existing file."""
        config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir)}}
        storage = FileSystemStorage(config)
        target = 'existing_file.txt'

        # Create existing file with different content
        existing_file = temp_dir / target
        existing_file.write_text('existing content')

        # Upload should overwrite
        storage.upload(str(temp_file), target)

        assert existing_file.read_text() == 'test content for upload'

    def test_file_permissions_preserved_on_upload(self, temp_dir, temp_file):
        """Test that file permissions are preserved during upload."""
        config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir)}}
        storage = FileSystemStorage(config)
        target = 'permission_test.txt'

        # Set specific permissions on source file
        os.chmod(temp_file, 0o644)

        storage.upload(str(temp_file), target)

        target_path = temp_dir / target
        # shutil.copy2 preserves permissions
        assert oct(target_path.stat().st_mode)[-3:] == '644'

    def test_error_handling_upload_nonexistent_source(self, temp_dir):
        """Test error handling when source file doesn't exist."""
        config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir)}}
        storage = FileSystemStorage(config)

        with pytest.raises(FileNotFoundError):
            storage.upload('nonexistent_source.txt', 'target.txt')

    def test_path_with_special_characters(self, temp_dir):
        """Test handling of paths with special characters."""
        config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir)}}
        storage = FileSystemStorage(config)

        # Create file with special characters in name
        special_file = temp_dir / 'file with spaces & symbols!.txt'
        special_file.write_text('special content')

        # Test exists
        assert storage.exists('file with spaces & symbols!.txt')

        # Test get_url
        url = storage.get_url('file with spaces & symbols!.txt')
        assert str(special_file.absolute()) in url

    def test_relative_path_resolution(self, temp_dir):
        """Test that relative paths are resolved correctly."""
        config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir)}}
        storage = FileSystemStorage(config)

        # Test with relative path components
        target = './subdir/../file.txt'
        test_file = temp_dir / 'source.txt'
        test_file.write_text('test content')

        storage.upload(str(test_file), target)

        # Should resolve to just "file.txt" in base directory
        assert (temp_dir / 'file.txt').exists()
        assert (temp_dir / 'file.txt').read_text() == 'test content'

    def test_empty_directory_file_count_and_size(self, temp_dir):
        """Test file count and size for empty directory."""
        empty_dir = temp_dir / 'empty'
        empty_dir.mkdir()

        config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir)}}
        storage = FileSystemStorage(config)
        empty_path = storage.get_pathlib('empty')

        assert storage.get_path_file_count(empty_path) == 0
        assert storage.get_path_total_size(empty_path) == 0

    def test_integration_with_get_storage_factory(self, temp_dir):
        """Test integration with storage factory function."""
        from synapse_sdk.utils.storage import get_storage

        config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir)}}
        storage = get_storage(config)

        assert isinstance(storage, FileSystemStorage)
        assert storage.base_path == temp_dir

    def test_nonexistent_base_path_handling(self):
        """Test behavior when base_path doesn't exist."""
        nonexistent_path = '/path/that/does/not/exist'
        config = {'provider': 'file_system', 'configuration': {'location': nonexistent_path}}

        # Should not raise error during initialization
        storage = FileSystemStorage(config)
        assert storage.base_path == Path(nonexistent_path)

        # Operations on non-existent paths should behave gracefully
        assert storage.exists('any_file.txt') is False

    def test_absolute_vs_relative_base_paths(self, temp_dir):
        """Test handling of absolute vs relative base paths."""
        # Test absolute path
        abs_config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir.absolute())}}
        abs_storage = FileSystemStorage(abs_config)
        assert abs_storage.base_path.is_absolute()

        # Test relative path
        rel_config = {'provider': 'file_system', 'configuration': {'location': '.'}}
        rel_storage = FileSystemStorage(rel_config)
        # Path object should still work correctly
        assert isinstance(rel_storage.base_path, Path)

    def test_path_normalization(self, temp_dir):
        """Test that paths are properly normalized."""
        config = {'provider': 'file_system', 'configuration': {'location': str(temp_dir) + '//extra//slashes//'}}
        storage = FileSystemStorage(config)

        # Create a test file
        test_file = temp_dir / 'source.txt'
        test_file.write_text('test content')

        # Upload should work despite extra slashes in base_path
        storage.upload(str(test_file), 'normal_target.txt')

        target_path = storage.base_path / 'normal_target.txt'
        assert target_path.exists()
