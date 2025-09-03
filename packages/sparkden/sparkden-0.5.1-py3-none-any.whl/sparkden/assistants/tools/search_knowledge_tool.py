from typing import Awaitable, Callable, Sequence

from google.adk.tools import FunctionTool, ToolContext

from sparkden.models.knowledge import DataChunk
from sparkden.services.knowledge import KnowledgeService


class SearchKnowledgeTool(FunctionTool):
    def __init__(self, collection_id: str):
        super().__init__(
            func=self.get_tool_func(collection_id),
        )

    @staticmethod
    def get_tool_func(
        collection_id: str,
    ) -> Callable[[str, ToolContext], Awaitable[Sequence[DataChunk]]]:
        async def search_knowledge(
            query: str, tool_context: ToolContext
        ) -> Sequence[DataChunk]:
            """Retrieve information from the knowledge collection.

            Args:
                query: The query to search for.

            Returns:
                A list of data chunks.
            """
            knowledge_service = KnowledgeService(
                user_id=tool_context._invocation_context.user_id
            )
            return await knowledge_service.search_collection(
                collection_id=collection_id,
                query=query,
            )

        return search_knowledge
