from upath import UPath

from synapse_sdk.utils.storage.providers import BaseStorage


class S3Storage(BaseStorage):
    ENDPOINT_URL = 'https://s3.amazonaws.com'
    DEFAULT_REGION = 'us-east-1'

    def __init__(self, url):
        super().__init__(url)

        self.upath = self._get_upath()

    def _get_upath(self):
        client_kwargs = {'region_name': self.query_params.get('region_name', self.DEFAULT_REGION)}

        if self.query_params.get('endpoint_url'):
            client_kwargs['endpoint_url'] = self.query_params['endpoint_url']

        upath_kwargs = {
            'key': self.query_params['access_key'],
            'secret': self.query_params['secret_key'],
            'client_kwargs': client_kwargs,
        }

        return UPath(
            f's3://{self.query_params["bucket_name"]}',
            **upath_kwargs,
        )

    def upload(self, source, target):
        with open(source, 'rb') as file:
            (self.upath / target).write_bytes(file.read())

        return self.get_url(target)

    def exists(self, target):
        return (self.upath / target).exists()

    def get_url(self, target):
        return str(self.upath.joinuri(target))

    def get_pathlib(self, path):
        return self.upath.joinuri(path)

    def get_path_file_count(self, pathlib_obj: UPath):
        """Get file count in the path from S3 provider.

        TODO: Need to find a method to get file count using S3 API

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
        """Get total size of the files in the path from S3 provider.

        TODO: Need to find a method to get total file size using S3 API

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

    def glob(self, pattern):
        """Glob pattern matching in S3 storage.

        Args:
            pattern (str): The glob pattern to match.

        Returns:
            list: List of matching paths.
        """
        return list((self.upath / '').glob(pattern))
