---
id: file
title: File Utilities
sidebar_position: 1
---

# File Utilities

File operations and handling utilities.

## File Operations

### Archive Functions

Functions for creating and extracting plugin archives.

### Download Functions

Utilities for downloading files from URLs.

```python
from synapse_sdk.utils.file import download_file

local_path = download_file(url, destination)
```

### Upload Functions

File upload utilities with chunked upload support.

## Chunked File Operations

### read_file_in_chunks

Read files in chunks for efficient memory usage, particularly useful for large files or when processing files in chunks for uploading or hashing.

```python
from synapse_sdk.utils.file import read_file_in_chunks

# Read a file in default 50MB chunks
for chunk in read_file_in_chunks('/path/to/large_file.bin'):
    process_chunk(chunk)

# Read with custom chunk size (10MB)
for chunk in read_file_in_chunks('/path/to/file.bin', chunk_size=1024*1024*10):
    upload_chunk(chunk)
```

**Parameters:**

- `file_path` (str | Path): Path to the file to read
- `chunk_size` (int, optional): Size of each chunk in bytes. Defaults to 50MB (52,428,800 bytes)

**Returns:**

- Generator yielding file content chunks as bytes

**Raises:**

- `FileNotFoundError`: If the file doesn't exist
- `PermissionError`: If the file can't be read due to permissions
- `OSError`: If there's an OS-level error reading the file

### Use Cases

**Large File Processing**: Efficiently process files that are too large to fit in memory:

```python
import hashlib

def calculate_hash_for_large_file(file_path):
    hash_md5 = hashlib.md5()
    for chunk in read_file_in_chunks(file_path):
        hash_md5.update(chunk)
    return hash_md5.hexdigest()
```

**Chunked Upload Integration**: The function integrates seamlessly with the `CoreClientMixin.create_chunked_upload` method:

```python
from synapse_sdk.clients.backend.core import CoreClientMixin

client = CoreClientMixin(base_url='https://api.example.com')
result = client.create_chunked_upload('/path/to/large_file.zip')
```

**Best Practices:**

- Use default chunk size (50MB) for optimal upload performance
- Adjust chunk size based on available memory and network conditions
- For very large files (>1GB), consider using smaller chunks for better progress tracking
- Always handle exceptions when working with file operations

## Checksum Functions

### get_checksum_from_file

Calculate checksum for file-like objects without requiring Django dependencies. This function works with any file-like object that has a `read()` method, making it compatible with Django's File objects, BytesIO, StringIO, and regular file objects.

```python
import hashlib
from io import BytesIO
from synapse_sdk.utils.file import get_checksum_from_file

# Basic usage with BytesIO (defaults to SHA1)
data = BytesIO(b'Hello, world!')
checksum = get_checksum_from_file(data)
print(checksum)  # SHA1 hash as hexadecimal string

# Using different hash algorithms
checksum_md5 = get_checksum_from_file(data, digest_mod=hashlib.md5)
checksum_sha256 = get_checksum_from_file(data, digest_mod=hashlib.sha256)

# With real file objects
with open('/path/to/file.txt', 'rb') as f:
    checksum = get_checksum_from_file(f)

# With StringIO (text files)
from io import StringIO
text_data = StringIO('Hello, world!')
checksum = get_checksum_from_file(text_data)  # Automatically UTF-8 encoded
```

**Parameters:**

- `file` (IO[Any]): File-like object with read() method that supports reading in chunks
- `digest_mod` (Callable[[], Any], optional): Hash algorithm from hashlib. Defaults to `hashlib.sha1`

**Returns:**

- `str`: Hexadecimal digest of the file contents

**Key Features:**

- **Memory Efficient**: Reads files in 4KB chunks to handle large files
- **Automatic File Pointer Reset**: Resets to beginning if the file object supports seeking
- **Text/Binary Agnostic**: Handles both text (StringIO) and binary (BytesIO) file objects
- **No Django Dependency**: Works without Django while being compatible with Django File objects
- **Flexible Hash Algorithms**: Supports any hashlib algorithm (SHA1, SHA256, MD5, etc.)

**Use Cases:**

**Django File Object Compatibility**: Works with Django's File objects without requiring Django:

```python
# Simulating Django File-like behavior
class FileWrapper:
    def __init__(self, data):
        self._data = data
        self._pos = 0

    def read(self, size=None):
        if size is None:
            result = self._data[self._pos:]
            self._pos = len(self._data)
        else:
            result = self._data[self._pos:self._pos + size]
            self._pos += len(result)
        return result

file_obj = FileWrapper(b'File content')
checksum = get_checksum_from_file(file_obj)
```

**Large File Processing**: Efficiently calculate checksums for large files:

```python
# Large file processing with memory efficiency
with open('/path/to/large_file.bin', 'rb') as large_file:
    checksum = get_checksum_from_file(large_file, digest_mod=hashlib.sha256)
```

**Multiple Hash Algorithms**: Calculate different checksums for the same file:

```python
algorithms = [
    ('MD5', hashlib.md5),
    ('SHA1', hashlib.sha1),
    ('SHA256', hashlib.sha256),
]

with open('/path/to/file.bin', 'rb') as f:
    checksums = {}
    for name, algo in algorithms:
        f.seek(0)  # Reset file pointer
        checksums[name] = get_checksum_from_file(f, digest_mod=algo)
```

## Path Utilities

Functions for path manipulation and validation.

## Temporary Files

Utilities for managing temporary files and cleanup.
