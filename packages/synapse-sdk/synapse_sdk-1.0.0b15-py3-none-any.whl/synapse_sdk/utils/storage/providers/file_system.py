import shutil
from pathlib import Path

from synapse_sdk.utils.storage.providers import BaseStorage


class FileSystemStorage(BaseStorage):
    """Storage provider for file system.

    * This storage do not support url based initialization.

    Args:
        url (str): The URL of the storage provider.

    Examples:
        >>> # Dict-based initialization
        >>> config = {
        ...     'provider': 'filesystem',
        ...     'configuration': {
        ...         'location': '/data'
        ...     }
        ... }
        >>> storage = FileSystemStorage(config)
    """

    def __init__(self, connection_params: str | dict):
        super().__init__(connection_params)
        self.base_path = Path(self.query_params['location'])

    def get_pathlib(self, path):
        """Get the path as a pathlib object.

        Args:
            path (str): The path to convert.

        Returns:
            pathlib.Path: The converted path.
        """
        if path == '/' or path == '':
            return self.base_path
        return self.base_path / path

    def upload(self, source, target):
        """Upload a file from source to target location.

        Args:
            source (str): Path to source file
            target (str): Target path relative to base path

        Returns:
            str: URL of uploaded file
        """
        source_path = Path(source)
        target_path = self.base_path / target

        # Create parent directories if they don't exist
        target_path.parent.mkdir(parents=True, exist_ok=True)

        # Copy the file
        shutil.copy2(source_path, target_path)

        return self.get_url(target)

    def exists(self, target):
        """Check if target file exists.

        Args:
            target (str): Target path relative to base path

        Returns:
            bool: True if file exists, False otherwise
        """
        target_path = self.base_path / target
        return target_path.exists()

    def get_url(self, target):
        """Get URL for target file.

        Args:
            target (str): Target path relative to base path

        Returns:
            str: File URL
        """
        target_path = self.base_path / target
        return f'file://{target_path.absolute()}'

    def get_path_file_count(self, pathlib_obj):
        """Get the file count in the path.

        Args:
            pathlib_obj (Path): The path to get file count.

        Returns:
            int: The file count in the path.
        """
        if not pathlib_obj.exists():
            return 0

        if pathlib_obj.is_file():
            return 1

        count = 0
        for item in pathlib_obj.rglob('*'):
            if item.is_file():
                count += 1
        return count

    def get_path_total_size(self, pathlib_obj):
        """Get the total size of the path.

        Args:
            pathlib_obj (Path): The path to get total size.

        Returns:
            int: The total size of the path.
        """
        if not pathlib_obj.exists():
            return 0

        if pathlib_obj.is_file():
            return pathlib_obj.stat().st_size

        total_size = 0
        for item in pathlib_obj.rglob('*'):
            if item.is_file():
                total_size += item.stat().st_size
        return total_size
