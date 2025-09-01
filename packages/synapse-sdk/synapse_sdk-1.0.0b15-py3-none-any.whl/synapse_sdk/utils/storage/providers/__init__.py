from urllib.parse import parse_qs, urlparse


class BaseStorage:
    """Base storage provider class for all storage implementations.

    This is an abstract base class that defines the interface for storage providers.
    All storage providers (S3, GCP, SFTP, HTTP, FileSystem) must inherit from this
    class and implement all the abstract methods.

    Args:
        connection_params (str | dict): The connection parameters. Can be either:
            - A URL string (e.g., 's3://bucket/path?access_key=key&secret_key=secret')
            - A dict with 'provider' and 'configuration' keys

    Attributes:
        url: Parsed URL object if connection_params was a string
        base_path: Base path for storage operations (provider-specific)
        options: Storage-specific options
        query_params: Parsed query parameters from URL or configuration dict
        OPTION_CASTS: Dictionary mapping option names to type casting functions

    Example:
        >>> # URL-based initialization
        >>> storage = SomeStorage('s3://bucket/path?access_key=key&secret_key=secret')
        >>>
        >>> # Dict-based initialization
        >>> config = {
        ...     'provider': 's3',
        ...     'configuration': {
        ...         'bucket_name': 'my-bucket',
        ...         'access_key': 'key',
        ...         'secret_key': 'secret'
        ...     }
        ... }
        >>> storage = SomeStorage(config)
    """

    url = None
    options = None
    OPTION_CASTS = {}

    def __init__(self, connection_params: str | dict):
        """Initialize the storage provider with connection parameters.

        Args:
            connection_params (str | dict): Connection parameters for the storage provider.
                If string, should be a valid URL with scheme and query parameters.
                If dict, should contain 'provider' and 'configuration' keys.
        """
        self.url = None

        if isinstance(connection_params, dict):
            self.query_params = connection_params['configuration']
        else:
            self.url = urlparse(connection_params)
            self.query_params = self.url_querystring_to_dict()

    def url_querystring_to_dict(self):
        """Parse URL query string into a dictionary with proper type casting.

        Converts query parameters from the URL into a dictionary, applying
        type casting based on OPTION_CASTS mapping. Single-value lists are
        flattened to scalar values.

        Returns:
            dict: Parsed and type-cast query parameters.
        """
        query_string = self.url.query

        query_dict = parse_qs(query_string)

        for key, value in query_dict.items():
            if len(value) == 1:
                query_dict[key] = value[0]

        return {
            key: self.OPTION_CASTS[key](value) if key in self.OPTION_CASTS else value
            for key, value in query_dict.items()
        }

    def upload(self, source, target):
        """Upload a file from source to target location.

        Args:
            source (str): Path to the source file on local filesystem.
            target (str): Target path in the storage provider.

        Returns:
            str: URL or identifier of the uploaded file.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def exists(self, target):
        """Check if a file exists at the target location.

        Args:
            target (str): Target path in the storage provider.

        Returns:
            bool: True if the file exists, False otherwise.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def get_url(self, target):
        """Get the URL for accessing a file at the target location.

        Args:
            target (str): Target path in the storage provider.

        Returns:
            str: URL that can be used to access the file.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.
        """
        raise NotImplementedError

    def get_pathlib(self, path):
        """Get the path as a pathlib-compatible object.

        Args:
            path (str): The path to convert, relative to the storage root.

        Returns:
            pathlib.Path or UPath: A pathlib-compatible object representing the path.
            The exact type depends on the storage provider implementation.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        Note:
            Different storage providers may return different path object types:
            - FileSystemStorage returns pathlib.Path objects
            - Cloud storage providers typically return UPath objects
        """
        raise NotImplementedError

    def get_path_file_count(self, pathlib_obj):
        """Get the total number of files in the given path.

        Args:
            pathlib_obj (Path | UPath): The path object to count files in.
                Should be obtained from get_pathlib().

        Returns:
            int: The total number of files found recursively in the path.
                Returns 1 for individual files, 0 for non-existent paths.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        Note:
            This method counts files recursively, including files in subdirectories.
            Directories themselves are not counted, only regular files.
        """
        raise NotImplementedError

    def get_path_total_size(self, pathlib_obj):
        """Get the total size of all files in the given path.

        Args:
            pathlib_obj (Path | UPath): The path object to calculate size for.
                Should be obtained from get_pathlib().

        Returns:
            int: The total size in bytes of all files found recursively in the path.
                Returns the file size for individual files, 0 for non-existent paths.

        Raises:
            NotImplementedError: This method must be implemented by subclasses.

        Note:
            This method calculates the total size recursively, including files
            in subdirectories. Only regular files contribute to the total size.
        """
        raise NotImplementedError
