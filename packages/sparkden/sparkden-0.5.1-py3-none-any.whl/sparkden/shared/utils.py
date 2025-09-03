import os
from typing import Any

from litestar.dto import DTOConfig
from pydantic.alias_generators import to_camel, to_snake


def getenv(key: str, default: str | None = None) -> str:
    value = os.getenv(key, default)
    if value is None:
        raise ValueError(f"Environment variable {key} is not defined")
    return value


def camelize_dict(data: dict[str, Any], recursive: bool = True) -> dict[str, Any]:
    if not recursive:
        return {to_camel(key): value for key, value in data.items()}

    def _camelize_value(value: Any) -> Any:
        if isinstance(value, dict):
            return camelize_dict(value, recursive=True)
        elif isinstance(value, list):
            return [_camelize_value(item) for item in value]
        return value

    return {to_camel(key): _camelize_value(value) for key, value in data.items()}


def snake_case_dict(data: dict[str, Any], recursive: bool = True) -> dict[str, Any]:
    if not recursive:
        return {to_snake(key): value for key, value in data.items()}

    def _snake_case_value(value: Any) -> Any:
        if isinstance(value, dict):
            return snake_case_dict(value, recursive=True)
        elif isinstance(value, list):
            return [_snake_case_value(item) for item in value]
        return value

    return {to_snake(key): _snake_case_value(value) for key, value in data.items()}


def dto_config(**kwargs) -> DTOConfig:
    default_kwargs = {
        "rename_strategy": "camel",
        "max_nested_depth": 100,
    }
    return DTOConfig(**default_kwargs, **kwargs)
