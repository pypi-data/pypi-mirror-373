from typing import Any, overload

import pydantic
from pydantic.alias_generators import to_camel

base_model_config = {
    "alias_generator": to_camel,
    "validate_by_alias": True,
    "validate_by_name": True,
    "from_attributes": True,
    "arbitrary_types_allowed": True,
}


class BaseModel(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(**base_model_config)


class OffsetPagination[ItemT](BaseModel):
    items: list[ItemT]
    total: int
    offset: int
    limit: int


class OrderBy(BaseModel):
    field: str
    desc: bool = True


class ExtraInfoMixin(BaseModel):
    extra_info: dict[str, Any] | None = None

    @overload
    def get_extra_info(self, key: str) -> Any: ...
    @overload
    def get_extra_info[T](self, key: str, default: T) -> T: ...

    def get_extra_info[T](self, key: str, default: T | None = None) -> T | None:
        return self.extra_info.get(key, default) if self.extra_info else default

    @overload
    def pop_extra_info(self, key: str) -> Any: ...
    @overload
    def pop_extra_info[T](self, key: str, default: T) -> T: ...

    def pop_extra_info[T](self, key: str, default: T | None = None) -> T | None:
        return self.extra_info.pop(key, default) if self.extra_info else default

    def set_extra_info(self, key: str, value: Any) -> None:
        if self.extra_info is None:
            self.extra_info = {}
        self.extra_info[key] = value
