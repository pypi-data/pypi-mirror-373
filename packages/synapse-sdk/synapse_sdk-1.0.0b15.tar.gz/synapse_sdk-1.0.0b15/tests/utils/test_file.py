"""
Tests for file utilities module.
"""

import hashlib
from io import BytesIO, StringIO
from unittest.mock import Mock, mock_open, patch

import pytest

from synapse_sdk.utils.file import get_checksum_from_file, read_file_in_chunks


class TestFileChunking:
    """Test file chunking utilities."""

    def test_read_small_file_single_chunk(self, tmp_path):
        """Test reading a small file that fits in a single chunk."""
        test_file = tmp_path / 'small_file.txt'
        test_content = b'Hello, world!'
        test_file.write_bytes(test_content)

        chunks = list(read_file_in_chunks(str(test_file)))

        assert len(chunks) == 1
        assert chunks[0] == test_content

    def test_read_large_file_multiple_chunks(self, tmp_path):
        """Test reading a large file that requires multiple chunks."""
        test_file = tmp_path / 'large_file.bin'
        chunk_size = 100  # Small chunk size for testing
        test_content = b'A' * 250  # Content that will span 3 chunks
        test_file.write_bytes(test_content)

        chunks = list(read_file_in_chunks(str(test_file), chunk_size=chunk_size))

        assert len(chunks) == 3
        assert chunks[0] == b'A' * 100
        assert chunks[1] == b'A' * 100
        assert chunks[2] == b'A' * 50

    def test_read_empty_file(self, tmp_path):
        """Test reading an empty file."""
        test_file = tmp_path / 'empty_file.txt'
        test_file.write_bytes(b'')

        chunks = list(read_file_in_chunks(str(test_file)))

        assert len(chunks) == 0

    def test_file_not_found_error(self):
        """Test that FileNotFoundError is raised for non-existent files."""
        with pytest.raises(FileNotFoundError):
            list(read_file_in_chunks('/non/existent/file.txt'))

    def test_permission_error(self):
        """Test that PermissionError is properly propagated."""
        with patch('builtins.open', mock_open()) as mock_file:
            mock_file.side_effect = PermissionError('Permission denied')

            with pytest.raises(PermissionError):
                list(read_file_in_chunks('/some/file.txt'))

    def test_custom_chunk_size(self, tmp_path):
        """Test reading with custom chunk sizes."""
        test_file = tmp_path / 'custom_chunk_test.bin'
        test_content = b'B' * 1000
        test_file.write_bytes(test_content)

        # Test with different chunk sizes
        chunk_sizes = [50, 200, 333, 1500]

        for chunk_size in chunk_sizes:
            chunks = list(read_file_in_chunks(str(test_file), chunk_size=chunk_size))
            reconstructed = b''.join(chunks)

            assert reconstructed == test_content
            if chunk_size >= 1000:
                assert len(chunks) == 1
            else:
                assert len(chunks) == (1000 + chunk_size - 1) // chunk_size  # Ceiling division

    def test_binary_file_reading(self, tmp_path):
        """Test reading binary files with various byte patterns."""
        test_file = tmp_path / 'binary_file.bin'
        # Create binary content with various byte values
        test_content = bytes(range(256)) * 4  # 1024 bytes with all possible byte values
        test_file.write_bytes(test_content)

        chunks = list(read_file_in_chunks(str(test_file), chunk_size=500))
        reconstructed = b''.join(chunks)

        assert reconstructed == test_content
        assert len(chunks) == 3  # 1024 bytes in 500-byte chunks = 3 chunks

    def test_path_object_input(self, tmp_path):
        """Test that Path objects work as input."""
        test_file = tmp_path / 'path_object_test.txt'
        test_content = b'Testing Path object input'
        test_file.write_bytes(test_content)

        # Test with Path object
        chunks = list(read_file_in_chunks(test_file))

        assert len(chunks) == 1
        assert chunks[0] == test_content

    def test_default_chunk_size(self):
        """Test that the default chunk size is 50MB."""
        test_content = b'Test default chunk size'

        with patch('builtins.open', mock_open()) as mock_file:
            mock_file_handle = Mock()
            # First call returns content, second call returns empty (EOF)
            mock_file_handle.read.side_effect = [test_content, b'']
            mock_file.return_value.__enter__.return_value = mock_file_handle

            # Convert generator to list to trigger the read
            chunks = list(read_file_in_chunks('dummy_file.txt'))

            # Verify the default chunk size was used (50MB = 1024 * 1024 * 50)
            expected_chunk_size = 1024 * 1024 * 50
            mock_file_handle.read.assert_called_with(expected_chunk_size)

            # Verify we got the expected content
            assert len(chunks) == 1
            assert chunks[0] == test_content

    def test_file_integrity_with_chunks(self, tmp_path):
        """Test that file content integrity is maintained across chunks."""
        test_file = tmp_path / 'integrity_test.bin'

        # Create content with a known pattern
        original_content = b''
        for i in range(1000):
            original_content += f'Line {i:04d} - Some test content\n'.encode()

        test_file.write_bytes(original_content)

        # Read with various chunk sizes and verify content integrity
        for chunk_size in [1024, 4096, 16384]:
            chunks = list(read_file_in_chunks(str(test_file), chunk_size=chunk_size))
            reconstructed = b''.join(chunks)

            assert reconstructed == original_content
            assert len(reconstructed) == len(original_content)


class TestChecksumFromFile:
    """Test checksum calculation from file-like objects."""

    def test_bytesio_default_sha1(self):
        """Test checksum calculation with BytesIO using default SHA1."""
        test_data = b'Hello, world!'
        file_obj = BytesIO(test_data)

        checksum = get_checksum_from_file(file_obj)

        # Verify against expected SHA1
        expected = hashlib.sha1(test_data).hexdigest()
        assert checksum == expected

    def test_bytesio_custom_hash_algorithm(self):
        """Test checksum with different hash algorithms."""
        test_data = b'Test data for hashing'

        algorithms = [
            (hashlib.md5, hashlib.md5(test_data).hexdigest()),
            (hashlib.sha1, hashlib.sha1(test_data).hexdigest()),
            (hashlib.sha256, hashlib.sha256(test_data).hexdigest()),
        ]

        for algo, expected in algorithms:
            file_obj = BytesIO(test_data)
            checksum = get_checksum_from_file(file_obj, digest_mod=algo)
            assert checksum == expected

    def test_stringio_text_handling(self):
        """Test handling of StringIO (text) objects."""
        test_text = 'Hello, world!'
        file_obj = StringIO(test_text)

        checksum = get_checksum_from_file(file_obj)

        # Should match SHA1 of UTF-8 encoded text
        expected = hashlib.sha1(test_text.encode('utf-8')).hexdigest()
        assert checksum == expected

    def test_empty_file(self):
        """Test checksum of empty file."""
        empty_file = BytesIO(b'')

        checksum = get_checksum_from_file(empty_file)

        # SHA1 of empty bytes
        expected = hashlib.sha1(b'').hexdigest()
        assert checksum == expected

    def test_large_file_chunked_reading(self):
        """Test that large files are processed in chunks correctly."""
        # Create large test data (larger than chunk size of 4096)
        large_data = b'A' * 10000
        file_obj = BytesIO(large_data)

        checksum = get_checksum_from_file(file_obj)

        # Verify against expected checksum
        expected = hashlib.sha1(large_data).hexdigest()
        assert checksum == expected

    def test_file_pointer_reset(self):
        """Test that file pointer is reset to beginning if seek is available."""
        test_data = b'Test data'
        file_obj = BytesIO(test_data)

        # Move file pointer to middle
        file_obj.read(4)
        assert file_obj.tell() == 4

        # Calculate checksum should reset pointer and read full content
        checksum = get_checksum_from_file(file_obj)

        expected = hashlib.sha1(test_data).hexdigest()
        assert checksum == expected

    def test_file_without_seek_method(self):
        """Test handling of file objects without seek method."""
        test_data = b'Test without seek'

        # Create mock file object without seek method
        mock_file = Mock()
        mock_file.read.side_effect = [test_data[:4], test_data[4:8], test_data[8:], b'']
        # Ensure hasattr returns False for seek
        del mock_file.seek

        checksum = get_checksum_from_file(mock_file)

        expected = hashlib.sha1(test_data).hexdigest()
        assert checksum == expected

    def test_binary_content_integrity(self):
        """Test checksum with various binary content patterns."""
        # Test with all possible byte values
        binary_data = bytes(range(256))
        file_obj = BytesIO(binary_data)

        checksum = get_checksum_from_file(file_obj)

        expected = hashlib.sha1(binary_data).hexdigest()
        assert checksum == expected

    def test_consistent_results_multiple_calls(self):
        """Test that multiple calls on same file return same checksum."""
        test_data = b'Consistency test data'

        checksums = []
        for _ in range(3):
            file_obj = BytesIO(test_data)
            checksum = get_checksum_from_file(file_obj)
            checksums.append(checksum)

        # All checksums should be identical
        assert len(set(checksums)) == 1
        assert checksums[0] == hashlib.sha1(test_data).hexdigest()

    def test_real_file_object(self, tmp_path):
        """Test with actual file objects from filesystem."""
        test_file = tmp_path / 'test_checksum.txt'
        test_content = b'File system test content'
        test_file.write_bytes(test_content)

        with open(test_file, 'rb') as f:
            checksum = get_checksum_from_file(f)

        expected = hashlib.sha1(test_content).hexdigest()
        assert checksum == expected

    def test_unicode_text_encoding(self):
        """Test handling of Unicode text in StringIO."""
        unicode_text = 'Hello, 世界! 🌍'
        file_obj = StringIO(unicode_text)

        checksum = get_checksum_from_file(file_obj)

        # Should match SHA1 of UTF-8 encoded Unicode text
        expected = hashlib.sha1(unicode_text.encode('utf-8')).hexdigest()
        assert checksum == expected
