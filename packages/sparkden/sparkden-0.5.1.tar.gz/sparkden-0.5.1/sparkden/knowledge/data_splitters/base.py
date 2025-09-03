from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sparkden.models.knowledge import DataChunk, ParseResult


class BaseDataSplitter(ABC):
    @abstractmethod
    async def split(self, data: "ParseResult") -> list["DataChunk"]:
        pass
