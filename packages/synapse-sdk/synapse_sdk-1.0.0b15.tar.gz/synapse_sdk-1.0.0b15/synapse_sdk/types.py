from typing import Any

from pydantic import HttpUrl
from pydantic_core import core_schema
from pydantic_core.core_schema import ValidationInfo

from synapse_sdk.utils.file import download_file, get_temp_path


class FileField(str):
    @classmethod
    def __get_pydantic_core_schema__(cls, source_type: Any, _handler: callable) -> core_schema.CoreSchema:
        return core_schema.with_info_before_validator_function(cls.validate, core_schema.str_schema())

    @staticmethod
    def validate(url: HttpUrl, info: ValidationInfo) -> str:
        path_download = get_temp_path('media')
        path_download.mkdir(parents=True, exist_ok=True)
        return str(download_file(url, path_download))
