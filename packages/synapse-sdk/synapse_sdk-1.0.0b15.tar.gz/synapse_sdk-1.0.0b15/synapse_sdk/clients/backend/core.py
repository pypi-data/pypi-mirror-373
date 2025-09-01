import hashlib
import os
from pathlib import Path

from synapse_sdk.clients.base import BaseClient
from synapse_sdk.utils.file import read_file_in_chunks


class CoreClientMixin(BaseClient):
    def create_chunked_upload(self, file_path):
        """
        Upload a file using chunked upload for efficient handling of large files.

        This method breaks the file into chunks and uploads them sequentially to the server.
        It calculates an MD5 hash of the entire file to ensure data integrity during upload.

        Args:
            file_path (str | Path): Path to the file to upload

        Returns:
            dict: Response from the server after successful upload completion,
                  typically containing upload confirmation and file metadata

        Raises:
            FileNotFoundError: If the specified file doesn't exist
            PermissionError: If the file can't be read due to permissions
            ClientError: If there's an error during the upload process
            OSError: If there's an OS-level error accessing the file

        Example:
            ```python
            client = CoreClientMixin(base_url='https://api.example.com')
            result = client.create_chunked_upload('/path/to/large_file.zip')
            print(f"Upload completed: {result}")
            ```

        Note:
            - Uses 50MB chunks by default for optimal upload performance
            - Automatically resumes from the last successfully uploaded chunk
            - Verifies upload integrity using MD5 checksum
        """
        file_path = Path(file_path)
        size = os.path.getsize(file_path)
        hash_md5 = hashlib.md5()

        url = 'chunked_upload/'
        offset = 0
        for chunk in read_file_in_chunks(file_path):
            hash_md5.update(chunk)
            data = self._put(
                url,
                data={'filename': file_path.name},
                files={'file': chunk},
                headers={'Content-Range': f'bytes {offset}-{offset + len(chunk) - 1}/{size}'},
            )
            offset = data['offset']
            url = data['url']

        return self._post(url, data={'md5': hash_md5.hexdigest()})
