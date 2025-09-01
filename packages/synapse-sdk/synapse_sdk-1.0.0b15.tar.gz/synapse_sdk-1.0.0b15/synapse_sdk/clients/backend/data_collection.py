from multiprocessing import Pool
from pathlib import Path
from typing import Dict, Optional, Union

from tqdm import tqdm

from synapse_sdk.clients.base import BaseClient
from synapse_sdk.clients.utils import get_batched_list, get_default_url_conversion


class DataCollectionClientMixin(BaseClient):
    """Mixin class for data collection operations.

    Provides methods for managing data collections, files, and units
    in the Synapse backend. Supports both regular file uploads and
    chunked uploads for large files.

    This mixin extends BaseClient with data collection-specific functionality
    including file upload capabilities, data unit management, and batch processing
    operations for efficient data collection workflows.
    """

    def list_data_collection(self):
        path = 'data_collections/'
        return self._list(path)

    def get_data_collection(self, data_collection_id):
        """Get data_collection from synapse-backend.

        Args:
            data_collection_id: The data_collection id to get.
        """
        path = f'data_collections/{data_collection_id}/?expand=file_specifications'
        return self._get(path)

    def create_data_file(
        self, file_path: Path, use_chunked_upload: bool = False
    ) -> Union[Dict[str, Union[str, int]], str]:
        """Create and upload a data file to the Synapse backend.

        This method supports two upload strategies:
        1. Direct file upload for smaller files (default)
        2. Chunked upload for large files (automatic when flag is enabled)

        Args:
            file_path: Path object pointing to the file to upload.
                Must be a valid file path that exists on the filesystem.
            use_chunked_upload: Boolean flag to enable chunked upload for the file.
                When True, automatically creates a chunked upload for the file
                instead of uploading it directly. Defaults to False.

        Returns:
            Dictionary containing the created data file information including:
                - id: The unique identifier of the created data file
                - checksum: The MD5 checksum of the uploaded file
                - size: The file size in bytes
                - created_at: Timestamp of creation
                - Additional metadata fields from the backend
            Or a string response in case of non-JSON response.

        Raises:
            FileNotFoundError: If the specified file doesn't exist (for direct upload)
            PermissionError: If the file can't be read due to permissions
            ClientError: If the backend returns an error response
            ValueError: If file_path is not a valid Path object

        Examples:
            Direct file upload for small files:
            ```python
            client = DataCollectionClientMixin(base_url='https://api.example.com')
            file_path = Path('/path/to/small_file.csv')
            result = client.create_data_file(file_path)
            print(f"File uploaded with ID: {result['id']}")
            ```

            Using chunked upload for large files:
            ```python
            # Automatically create chunked upload for large file
            file_path = Path('/path/to/large_file.zip')
            result = client.create_data_file(file_path, use_chunked_upload=True)
            print(f"Large file uploaded with ID: {result['id']}")
            ```

        Note:
            - For files larger than 100MB, consider using chunked upload
            - The chunked upload will be automatically created when the flag is enabled
            - Chunked uploads provide better reliability for large files
        """
        path = 'data_files/'
        if use_chunked_upload:
            chunked_upload = self.create_chunked_upload(file_path)
            data = {'chunked_upload': chunked_upload['id']}
            return self._post(path, data=data)
        else:
            return self._post(path, files={'file': file_path})

    def get_data_unit(self, data_unit_id: int, params=None):
        path = f'data_units/{data_unit_id}/'
        return self._get(path, params=params)

    def create_data_units(self, data):
        """Create data units to synapse-backend.

        Args:
            data: The data bindings to upload from create_data_file interface.
        """
        path = 'data_units/'
        return self._post(path, data=data)

    def list_data_units(self, params=None, url_conversion=None, list_all=False):
        path = 'data_units/'
        url_conversion = get_default_url_conversion(url_conversion, files_fields=['files'])
        return self._list(path, params=params, url_conversion=url_conversion, list_all=list_all)

    def data_file_verify_checksums(self, checksums: list[str]):
        """Check checksums from files are exists.

        Args:
            checksums: A list of MD5 checksums to verify.
        """
        path = 'data_file/verify_checksums/'
        data = {'checksums': checksums}
        return self._post(path, data=data)

    def upload_data_collection(
        self,
        data_collection_id: int,
        data_collection: Dict,
        project_id: Optional[int] = None,
        batch_size: int = 1000,
        process_pool: int = 10,
    ):
        """Upload data_collection to synapse-backend.

        Args:
            data_collection_id: The data_collection id to upload the data to.
            data_collection: The data_collection to upload.
                * structure:
                    - files: The files to upload. (key: file name, value: file pathlib object)
                    - meta: The meta data to upload.
            project_id: The project id to upload the data to.
            batch_size: The batch size to upload the data.
            process_pool: The process pool to upload the data.
        """
        # TODO validate data_collection with schema

        params = [(data, data_collection_id) for data in data_collection]

        with Pool(processes=process_pool) as pool:
            data_collection = pool.starmap(self.upload_data_file, tqdm(params))

        batches = get_batched_list(data_collection, batch_size)

        for batch in tqdm(batches):
            data_units = self.create_data_units(batch)

            if project_id:
                tasks_data = []
                for data, data_unit in zip(batch, data_units):
                    task_data = {'project': project_id, 'data_unit': data_unit['id']}
                    # TODO: Additional logic needed here if task data storage is required during import.

                    tasks_data.append(task_data)

                self.create_tasks(tasks_data)

    def upload_data_file(self, data: Dict, data_collection_id: int) -> Dict:
        """Upload files to synapse-backend.

        Args:
            data: The data to upload.
                * structure:
                    - files: The files to upload. (key: file name, value: file pathlib object)
                    - meta: The meta data to upload.
            data_collection_id: The data_collection id to upload the data to.

        Returns:
            Dict: The result of the upload.
        """
        for name, path in data['files'].items():
            data_file = self.create_data_file(path)
            data['data_collection'] = data_collection_id
            data['files'][name] = {'checksum': data_file['checksum'], 'path': str(path)}
        return data
