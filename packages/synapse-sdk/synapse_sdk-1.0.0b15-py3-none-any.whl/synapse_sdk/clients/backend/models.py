from enum import Enum
from typing import Dict, Optional

from pydantic import BaseModel


class StorageCategory(str, Enum):
    """Synapse Backend Storage Category Enum."""

    INTERNAL = 'internal'
    EXTERNAL = 'external'


class StorageProvider(str, Enum):
    """Synapse Backend Storage Provider Enum."""

    AMAZON_S3 = 'amazon_s3'
    AZURE = 'azure'
    DIGITAL_OCEAN = 'digital_ocean'
    FILE_SYSTEM = 'file_system'
    FTP = 'ftp'
    SFTP = 'sftp'
    MINIO = 'minio'
    GCP = 'gcp'


class Storage(BaseModel):
    """Synapse Backend Storage Model.

    Attrs:
        id (int): The storage pk.
        name (str): The storage name.
        category (str): The storage category. (ex: internal, external)
        provider (str): The storage provider. (ex: s3, gcp)
        configuration (Dict): The storage configuration.
        is_default (bool): The storage is default for Synapse backend workspace.
    """

    id: int
    name: str
    category: StorageCategory
    provider: StorageProvider
    configuration: Dict
    is_default: bool


class JobStatus(str, Enum):
    """Synapse Backend Job Status Enum."""

    PENDING = 'pending'
    RUNNING = 'running'
    STOPPED = 'stopped'
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'


class UpdateJob(BaseModel):
    """Synapse Backend Update Job Request Payload Model.

    Attrs:
        status (str): The job status. (ex: pending, running, stopped, succeeded, failed)
        progress_record (Dict): The job progress record.
        metrics_record (Dict): The job metrics record.
        console_logs (Dict): The job console logs.
        result (Dict): The job result.
    """

    status: Optional[JobStatus] = None
    progress_record: Optional[Dict] = None
    metrics_record: Optional[Dict] = None
    console_logs: Optional[Dict | list] = None
    result: Optional[Dict | list] = None

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        if data.get('status') is not None:
            data['status'] = data['status'].value
        return data
