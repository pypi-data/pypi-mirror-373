from sparkden.db.schema import DataSourceStatus
from sparkden.knowledge.data_loader import DataLoader
from sparkden.knowledge.registry import knowledge_collections
from sparkden.knowledge.vector_store.base import (
    FieldCondition,
    Filter,
    MatchValue,
)
from sparkden.queued_job.decorator import JobContext, JobResult, queued_job
from sparkden.services.knowledge import KnowledgeService


@queued_job(queue_name="search_context")
async def search_context_job(
    ctx: JobContext,
    data_source_id: str,
    query: str,
) -> JobResult:
    """
    Asynchronously processes a data source, including loading, parsing,
    embedding, and indexing.
    """
    knowledge_service = KnowledgeService(user_id=ctx.user_id)

    try:
        await ctx.update_progress(5, custom_status="initializing")

        data_source = await knowledge_service.get_data_source(data_source_id)
        if not data_source:
            raise ValueError(f"Data source {data_source_id} not found")

        if data_source.status != DataSourceStatus.READY:
            collection = knowledge_collections.get_collection(data_source.collection_id)
            if not collection:
                raise ValueError(f"Collection {data_source.collection_id} not found")

            loader = DataLoader(
                data_source=data_source,
                vector_dimensions=collection.vector_dimensions,
                retrieval_mode=collection.retrieval_mode,
            )

            async for status in loader.load():
                await ctx.update_progress(30, custom_status=status)

            await knowledge_service.update_data_source(
                data_source_id, {"status": DataSourceStatus.READY}
            )

        await ctx.update_progress(90, custom_status="retrieving")

        filter = Filter(
            must=[
                FieldCondition(
                    key="data_source_id",
                    match=MatchValue(value=data_source_id),
                ),
            ],
        )
        data_chunks = await knowledge_service.search_collection(
            collection_id=data_source.collection_id,
            query=query,
            filter=filter,
        )

        await ctx.update_progress(100, custom_status="completed")

        return {
            "data_chunks": [chunk.model_dump() for chunk in data_chunks],
            "data_source_creator_id": data_source.creator_id,
            "data_source_name": data_source.name,
        }

    except Exception as e:
        # Update data source status to ERROR on failure
        await knowledge_service.update_data_source(
            data_source_id, {"status": DataSourceStatus.ERROR}
        )
        # Re-raise the exception so the job is marked as failed
        raise e
