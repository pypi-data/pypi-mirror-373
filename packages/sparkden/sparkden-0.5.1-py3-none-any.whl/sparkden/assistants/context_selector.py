from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from sparkden.models.assistant import ContextOption


class ContextSelector(ABC):
    @abstractmethod
    async def context_options(
        self, user_id: str, search_query: str | None = None
    ) -> "list[ContextOption]":
        pass
