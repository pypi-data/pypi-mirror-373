from google.adk.tools import ToolContext

from sparkden.assistants.helpers import assistant_context_collection_id
from sparkden.db.schema import DataSourceStatus
from sparkden.knowledge.vector_store.base import (
    FieldCondition,
    Filter,
    MatchValue,
)
from sparkden.models.assistant import ToolResponse, ToolResponseStatus
from sparkden.queued_job.search_context_job import search_context_job
from sparkden.services.knowledge import KnowledgeService


async def search_context(
    data_source_id: str, query: str, tool_context: ToolContext
) -> ToolResponse:
    """Retrieve information from context with data_source_id.

    Args:
        query: The query to search for.

    Returns:
        A list of data chunks.
    """
    user_id = tool_context._invocation_context.user_id
    knowledge_service = KnowledgeService(user_id=user_id)

    try:
        data_source = await knowledge_service.get_data_source(data_source_id)
    except Exception:
        return ToolResponse(
            status=ToolResponseStatus.ERROR,
            error=f"Failed to get data source with id {data_source_id}",
        )

    if not data_source:
        return ToolResponse(
            status=ToolResponseStatus.ERROR,
            error=f"Data source {data_source_id} not found",
        )

    if data_source.status != DataSourceStatus.READY:
        tool_context.actions.skip_summarization = True

        message = search_context_job.send(
            data_source_id=data_source_id,
            query=query,
            user_id=user_id,
        )
        job_id = message.message_id

        return ToolResponse(
            result={
                "job_id": job_id,
                "data_source_creator_id": data_source.creator_id,
                "data_source_name": data_source.name,
            },
            status=ToolResponseStatus.PENDING,
        )

    filter = Filter(
        must=[
            FieldCondition(
                key="data_source_id",
                match=MatchValue(value=data_source_id),
            ),
        ],
    )
    data_chunks = await knowledge_service.search_collection(
        collection_id=assistant_context_collection_id(
            tool_context._invocation_context.app_name
        ),
        query=query,
        filter=filter,
    )

    return ToolResponse(
        result={
            "data_chunks": data_chunks,
            "data_source_creator_id": data_source.creator_id,
            "data_source_name": data_source.name,
        },
        status=ToolResponseStatus.SUCCESS,
    )
