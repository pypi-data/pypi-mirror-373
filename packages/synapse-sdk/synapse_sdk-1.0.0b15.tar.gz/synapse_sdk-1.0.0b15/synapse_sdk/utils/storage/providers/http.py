import os
from urllib.parse import urljoin, urlparse

import requests

from synapse_sdk.utils.storage.providers import BaseStorage


class HTTPStorage(BaseStorage):
    """Storage provider for no-auth HTTP file servers (e.g., Django FileSystemStorage served over HTTP)."""

    OPTION_CASTS = {
        'timeout': int,
    }

    def __init__(self, connection_params: str | dict):
        super().__init__(connection_params)

        # Extract base URL
        if isinstance(connection_params, dict):
            self.base_url = self.query_params.get('base_url', '')
            self.timeout = self.query_params.get('timeout', 30)
        else:
            # Parse URL like: http://example.com/media/
            parsed = urlparse(connection_params)
            self.base_url = f'{parsed.scheme}://{parsed.netloc}{parsed.path}'
            self.timeout = self.query_params.get('timeout', 30)

        # Ensure base_url ends with /
        if not self.base_url.endswith('/'):
            self.base_url += '/'

        # Setup session for connection pooling
        self.session = requests.Session()

    def _get_full_url(self, path: str) -> str:
        """Get the full URL for a given path."""
        # Remove leading slash from path to avoid double slashes
        if path.startswith('/'):
            path = path[1:]
        return urljoin(self.base_url, path)

    def upload(self, source: str, target: str) -> str:
        """Upload a file to the HTTP server.

        Args:
            source: Local file path to upload
            target: Target path on the HTTP server

        Returns:
            URL of the uploaded file
        """
        url = self._get_full_url(target)

        with open(source, 'rb') as f:
            files = {'file': (os.path.basename(source), f)}

            # Try PUT first (more RESTful), fallback to POST
            response = self.session.put(url, files=files, timeout=self.timeout)

            if response.status_code == 405:  # Method not allowed
                # Reset file pointer and try POST
                f.seek(0)
                response = self.session.post(url, files=files, timeout=self.timeout)

            response.raise_for_status()

        return url

    def exists(self, target: str) -> bool:
        """Check if a file exists on the HTTP server.

        Args:
            target: Path to check

        Returns:
            True if file exists, False otherwise
        """
        url = self._get_full_url(target)

        try:
            response = self.session.head(url, timeout=self.timeout)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def get_url(self, target: str) -> str:
        """Get the URL for a file.

        Args:
            target: File path

        Returns:
            Full URL of the file
        """
        return self._get_full_url(target)

    def get_pathlib(self, path: str) -> 'HTTPPath':
        """Get a pathlib-like object for HTTP operations.

        Args:
            path: Path to wrap

        Returns:
            HTTPPath object
        """
        return HTTPPath(self, path)

    def get_path_file_count(self, pathlib_obj) -> int:
        """Get file count in a directory.

        Note: This requires the HTTP server to provide directory listing functionality.

        Args:
            pathlib_obj: HTTPPath object

        Returns:
            File count
        """
        # Most HTTP servers don't provide directory listing
        # This would need custom server-side support
        raise NotImplementedError('File counting requires server-side directory listing support')

    def get_path_total_size(self, pathlib_obj) -> int:
        """Get total size of files in a directory.

        Note: This requires the HTTP server to provide directory listing functionality.

        Args:
            pathlib_obj: HTTPPath object

        Returns:
            Total size in bytes
        """
        # Most HTTP servers don't provide directory listing
        # This would need custom server-side support
        raise NotImplementedError('Size calculation requires server-side directory listing support')


class HTTPPath:
    """A pathlib-like interface for HTTP paths."""

    def __init__(self, storage: HTTPStorage, path: str):
        self.storage = storage
        self.path = path.strip('/')

    def __str__(self):
        return self.path

    def __truediv__(self, other):
        """Join paths using / operator."""
        new_path = f'{self.path}/{other}' if self.path else str(other)
        return HTTPPath(self.storage, new_path)

    def joinuri(self, *parts):
        """Join path parts."""
        parts = [self.path] + [str(p) for p in parts]
        new_path = '/'.join(p.strip('/') for p in parts if p)
        return HTTPPath(self.storage, new_path)

    @property
    def name(self):
        """Get the final component of the path."""
        return os.path.basename(self.path)

    @property
    def parent(self):
        """Get the parent directory."""
        parent_path = os.path.dirname(self.path)
        return HTTPPath(self.storage, parent_path)

    def exists(self):
        """Check if this path exists."""
        return self.storage.exists(self.path)

    def is_file(self):
        """Check if this path is a file."""
        # For HTTP, we assume it's a file if it exists
        return self.exists()

    def read_bytes(self):
        """Read file contents as bytes."""
        url = self.storage.get_url(self.path)
        response = self.storage.session.get(url, timeout=self.storage.timeout)
        response.raise_for_status()
        return response.content

    def read_text(self, encoding='utf-8'):
        """Read file contents as text."""
        return self.read_bytes().decode(encoding)
