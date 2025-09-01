from pathlib import Path
from urllib.parse import urlparse

from synapse_sdk.i18n import gettext as _
from synapse_sdk.utils.storage.registry import STORAGE_PROVIDERS


def get_storage(connection_param: str | dict):
    """Get storage class with connection param.

    Args:
        connection_param (str | dict): The connection param for the Storage provider.

    Returns:
        BaseStorage: The storage class object with connection param.
    """
    storage_scheme = None
    if isinstance(connection_param, dict):
        storage_scheme = connection_param['provider']
    else:
        storage_scheme = urlparse(connection_param).scheme

    assert storage_scheme in STORAGE_PROVIDERS.keys(), _('Storage provider not supported.')
    return STORAGE_PROVIDERS[storage_scheme](connection_param)


def get_pathlib(storage_config: str | dict, path_root: str) -> Path:
    """Get pathlib object with synapse-backend storage config.

    Args:
        storage_config (str | dict): The storage config by synapse-backend storage api.
        path_root (str): The path root.

    Returns:
        pathlib.Path: The pathlib object.
    """
    storage_class = get_storage(storage_config)
    return storage_class.get_pathlib(path_root)


def get_path_file_count(storage_config: str | dict, path_root: str) -> int:
    """Get the file count in the path.

    Args:
        storage_config (str | dict): The storage config by synapse-backend storage api.
        path (str): The path.

    Returns:
        int: The file count in the path.
    """
    storage_class = get_storage(storage_config)
    pathlib_obj = storage_class.get_pathlib(path_root)
    return storage_class.get_path_file_count(pathlib_obj)


def get_path_total_size(storage_config: str | dict, path_root: str) -> int:
    """Get total size of the files in the path.

    Args:
        storage_config (str | dict): The storage config by synapse-backend storage api.
        path (str): The path.

    Returns:
        int: The total size of the files in the path.
    """
    storage_class = get_storage(storage_config)
    pathlib_obj = storage_class.get_pathlib(path_root)
    return storage_class.get_path_total_size(pathlib_obj)
