from upath import UPath

from synapse_sdk.utils.storage.providers import BaseStorage


class SFTPStorage(BaseStorage):
    def get_pathlib(self, path):
        credentials = self.query_params['params']
        host = self.query_params['host']
        root_path = self.query_params['root_path']

        username = credentials['username']
        password = credentials['password']
        if path == '/':
            path = ''
        return UPath(f'sftp://{host}', username=username, password=password) / root_path / path

    def get_path_file_count(self, pathlib_obj: UPath):
        """Get file count in the path from SFTP provider.

        Args:
            pathlib_obj (UPath): The path to get file count.

        Returns:
            int: The file count in the path.
        """
        count = 0
        files = list(pathlib_obj.glob('**/*'))
        for file in files:
            if file.is_file():
                count += 1
        return count

    def get_path_total_size(self, pathlib_obj: UPath):
        """Get total size of the files in the path from SFTP provider.

        Args:
            pathlib_obj (UPath): The path to get total size.

        Returns:
            int: The total size of the files in the path.
        """
        total_size = 0
        for file in pathlib_obj.glob('**/*'):
            if file.is_file():
                total_size += file.stat().st_size
        return total_size
