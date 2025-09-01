import asyncio
import base64
import hashlib
import json
import mimetypes
import operator
import zipfile
from functools import reduce
from pathlib import Path
from typing import IO, Any, Callable

import aiohttp
import requests
import yaml

from synapse_sdk.utils.network import clean_url
from synapse_sdk.utils.string import hash_text


def read_file_in_chunks(file_path, chunk_size=1024 * 1024 * 50):
    """
    Read a file in chunks for efficient memory usage during file processing.

    This function is particularly useful for large files or when you need to process
    files in chunks, such as for uploading or hashing.

    Args:
        file_path (str | Path): Path to the file to read
        chunk_size (int, optional): Size of each chunk in bytes. Defaults to 50MB (1024 * 1024 * 50)

    Yields:
        bytes: File content chunks

    Raises:
        FileNotFoundError: If the file doesn't exist
        PermissionError: If the file can't be read due to permissions
        OSError: If there's an OS-level error reading the file

    Example:
        ```python
        from synapse_sdk.utils.file import read_file_in_chunks

        # Read a file in 10MB chunks
        for chunk in read_file_in_chunks('large_file.bin', chunk_size=1024*1024*10):
            process_chunk(chunk)
        ```
    """
    with open(file_path, 'rb') as file:
        while chunk := file.read(chunk_size):
            yield chunk


def download_file(url, path_download, name=None, coerce=None, use_cached=True):
    chunk_size = 1024 * 1024 * 50
    cleaned_url = clean_url(url)  # remove query params and fragment

    if name:
        use_cached = False
    else:
        name = hash_text(cleaned_url)

    name += Path(cleaned_url).suffix

    path = Path(path_download) / name

    if not use_cached or not path.is_file():
        response = requests.get(url, allow_redirects=True, stream=True)
        response.raise_for_status()

        with path.open('wb') as file:
            for chunk in response.iter_content(chunk_size=chunk_size):
                file.write(chunk)

    if coerce:
        path = coerce(path)

    return path


def files_url_to_path(files, coerce=None, file_field=None):
    path_download = get_temp_path('media')
    path_download.mkdir(parents=True, exist_ok=True)
    if file_field:
        files[file_field] = download_file(files[file_field], path_download, coerce=coerce)
    else:
        for file_name in files:
            if isinstance(files[file_name], str):
                files[file_name] = download_file(files[file_name], path_download, coerce=coerce)
            else:
                files[file_name]['path'] = download_file(files[file_name].pop('url'), path_download, coerce=coerce)


def files_url_to_path_from_objs(objs, files_fields, coerce=None, is_list=False, is_async=False):
    if is_async:
        asyncio.run(afiles_url_to_path_from_objs(objs, files_fields, coerce=coerce, is_list=is_list))
    else:
        if not is_list:
            objs = [objs]

        for obj in objs:
            for files_field in files_fields:
                try:
                    files = reduce(operator.getitem, files_field.split('.'), obj)
                    if isinstance(files, str):
                        files_url_to_path(obj, coerce=coerce, file_field=files_field)
                    else:
                        files_url_to_path(files, coerce=coerce)
                except KeyError:
                    pass


async def adownload_file(url, path_download, name=None, coerce=None, use_cached=True):
    chunk_size = 1024 * 1024 * 50
    cleaned_url = clean_url(url)  # remove query params and fragment

    if name:
        use_cached = False
    else:
        name = hash_text(cleaned_url)

    name += Path(cleaned_url).suffix

    path = Path(path_download) / name

    if not use_cached or not path.is_file():
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                with path.open('wb') as file:
                    while chunk := await response.content.read(chunk_size):
                        file.write(chunk)

    if coerce:
        path = coerce(path)

    return path


async def afiles_url_to_path(files, coerce=None):
    path_download = get_temp_path('media')
    path_download.mkdir(parents=True, exist_ok=True)
    for file_name in files:
        if isinstance(files[file_name], str):
            files[file_name] = await adownload_file(files[file_name], path_download, coerce=coerce)
        else:
            files[file_name]['path'] = await adownload_file(files[file_name].pop('url'), path_download, coerce=coerce)


async def afiles_url_to_path_from_objs(objs, files_fields, coerce=None, is_list=False):
    if not is_list:
        objs = [objs]

    tasks = []

    for obj in objs:
        for files_field in files_fields:
            try:
                files = reduce(operator.getitem, files_field.split('.'), obj)
                tasks.append(afiles_url_to_path(files, coerce=coerce))
            except KeyError:
                pass

    await asyncio.gather(*tasks)


def get_dict_from_file(file_path):
    if isinstance(file_path, str):
        file_path = Path(file_path)

    with open(file_path) as f:
        if file_path.suffix == '.yaml':
            return yaml.safe_load(f)
        else:
            return json.load(f)


def calculate_checksum(file_path, prefix=''):
    md5_hash = hashlib.md5()
    with open(file_path, 'rb') as f:
        for byte_block in iter(lambda: f.read(4096), b''):
            md5_hash.update(byte_block)
    checksum = md5_hash.hexdigest()
    if prefix:
        return f'dev-{checksum}'
    return checksum


def get_checksum_from_file(file: IO[Any], digest_mod: Callable[[], Any] = hashlib.sha1) -> str:
    """
    Calculate checksum for a file-like object.

    Args:
        file (IO[Any]): File-like object with read() method that supports reading in chunks
        digest_mod (Callable[[], Any]): Hash algorithm from hashlib (defaults to hashlib.sha1)

    Returns:
        str: Hexadecimal digest of the file contents

    Example:
        ```python
        import hashlib
        from io import BytesIO
        from synapse_sdk.utils.file import get_checksum_from_file

        # With BytesIO
        data = BytesIO(b'Hello, world!')
        checksum = get_checksum_from_file(data)

        # With different hash algorithm
        checksum = get_checksum_from_file(data, digest_mod=hashlib.sha256)
        ```
    """
    digest = digest_mod()
    chunk_size = 4096

    # Reset file pointer to beginning if possible
    if hasattr(file, 'seek'):
        file.seek(0)

    while True:
        chunk = file.read(chunk_size)
        if not chunk:
            break
        if isinstance(chunk, str):
            chunk = chunk.encode('utf-8')
        digest.update(chunk)

    return digest.hexdigest()


def archive(input_path, output_path, append=False):
    input_path = Path(input_path)
    output_path = Path(output_path)

    mode = 'a' if append and output_path.exists() else 'w'
    with zipfile.ZipFile(output_path, mode=mode, compression=zipfile.ZIP_DEFLATED) as zipf:
        if input_path.is_file():
            zipf.write(input_path, input_path.name)
        else:
            for file_path in input_path.rglob('*'):
                if file_path.is_file():  # Only add files, skip directories
                    arcname = file_path.relative_to(input_path.parent)
                    zipf.write(file_path, arcname)


def unarchive(file_path, output_path):
    """
    Unarchives a ZIP file to a given directory.

    Parameters:
        file_path (str | Path): The path to the ZIP file.
        output_path (str): The directory where the files will be extracted.
    """
    output_path = Path(output_path)
    output_path.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(str(file_path), 'r') as zip_ref:
        zip_ref.extractall(output_path)


def get_temp_path(sub_path=None):
    path = Path('/tmp/datamaker')
    if sub_path:
        path = path / sub_path
    return path


def convert_file_to_base64(file_path):
    """
    Convert a file to base64 using pathlib.

    Args:
        file_path (str): Path to the file to convert

    Returns:
        str: Base64 encoded string of the file contents
    """
    # FIXME base64 is sent sometimes.
    if file_path.startswith('data:'):
        return file_path

    # Convert string path to Path object
    path = Path(file_path)

    try:
        # Read binary content of the file
        binary_content = path.read_bytes()

        # Convert to base64
        base64_encoded = base64.b64encode(binary_content).decode('utf-8')

        # Get the MIME type of the file
        mime_type, _ = mimetypes.guess_type(path)
        assert mime_type is not None, 'MIME type cannot be guessed'

        # Convert bytes to string for readable output
        return f'data:{mime_type};base64,{base64_encoded}'

    except FileNotFoundError:
        raise FileNotFoundError(f'File not found: {file_path}')
    except Exception as e:
        raise Exception(f'Error converting file to base64: {str(e)}')
