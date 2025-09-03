from sparkden.db.schema import DataSourceStatus
from sparkden.knowledge.data_loader import DataLoader
from sparkden.knowledge.registry import knowledge_collections
from sparkden.queued_job.decorator import JobContext, JobResult, queued_job
from sparkden.services.knowledge.data_source import KnowledgeDataSourceService


@queued_job(queue_name="knowledge")
async def data_source_job(
    ctx: JobContext,
    data_source_id: str,
    reload: bool = False,
) -> JobResult:
    """
    Asynchronously processes a data source, including loading, parsing,
    embedding, and indexing.
    """
    data_source_service = KnowledgeDataSourceService(user_id=ctx.user_id)

    try:
        await ctx.update_progress(5, custom_status="initializing")

        data_source = await data_source_service.get_data_source(data_source_id)
        if not data_source:
            raise ValueError(f"Data source {data_source_id} not found")

        collection = knowledge_collections.get_collection(data_source.collection_id)
        if not collection:
            raise ValueError(f"Collection {data_source.collection_id} not found")

        loader = DataLoader(
            data_source=data_source,
            vector_dimensions=collection.vector_dimensions,
            retrieval_mode=collection.retrieval_mode,
        )

        if reload:
            async for status in loader.reload():
                await ctx.update_progress(30, custom_status=status)
        else:
            async for status in loader.load():
                await ctx.update_progress(30, custom_status=status)

        await data_source_service.update_data_source(
            data_source_id, {"status": DataSourceStatus.READY}
        )
        await ctx.update_progress(100, custom_status="completed")

        return {"data_source_id": data_source_id}

    except Exception as e:
        # Update data source status to ERROR on failure
        await data_source_service.update_data_source(
            data_source_id, {"status": DataSourceStatus.ERROR}
        )
        # Re-raise the exception so the job is marked as failed
        raise e
