from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Any, Type

from sparkden.models.shared import BaseModel

if TYPE_CHECKING:
    from sparkden.models.knowledge import FileExtractConfig, ParseResult


class BaseDataParser[DataType: BaseModel](ABC):
    def __init__(self, input_data_type: Type[DataType]):
        self.input_data_type = input_data_type

    def _parse_input_data(self, input_data: dict[str, Any] | DataType) -> DataType:
        if isinstance(input_data, dict):
            return self.input_data_type.model_validate(input_data)
        else:
            return input_data

    @abstractmethod
    async def parse(
        self,
        input_data: dict[str, Any] | DataType,
        file_extract_config: "FileExtractConfig",
    ) -> "ParseResult":
        pass
