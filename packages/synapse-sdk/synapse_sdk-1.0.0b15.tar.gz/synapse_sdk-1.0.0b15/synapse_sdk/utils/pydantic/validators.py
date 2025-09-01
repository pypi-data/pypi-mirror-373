from pydantic_core import PydanticCustomError


def non_blank(value):
    if not value.strip():
        raise PydanticCustomError('blank', '필수 값을 확인해주세요.')
    return value
