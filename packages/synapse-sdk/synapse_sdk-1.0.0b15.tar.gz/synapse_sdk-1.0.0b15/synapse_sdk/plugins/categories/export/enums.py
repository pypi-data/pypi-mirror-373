from enum import Enum


class ExportStatus(str, Enum):
    SUCCESS = 'success'
    FAILED = 'failed'
    STAND_BY = 'stand_by'
