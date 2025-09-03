from typing import Any, cast

from sparkden.db.schema import DataSourceStatus
from sparkden.db.schema import KnowledgeDataSource as StorageDataSource
from sparkden.knowledge.data_loader import DataLoader
from sparkden.knowledge.registry import knowledge_collections
from sparkden.knowledge.vector_store import (
    FieldCondition,
    Filter,
    MatchValue,
    VectorStore,
)
from sparkden.models.knowledge import (
    DataChunk,
    DataSourceCreatorType,
    FileObject,
    KnowledgeDataSource,
    KnowledgeDataSourceCreate,
)
from sparkden.models.shared import OffsetPagination, OrderBy
from sparkden.services.base import BaseService
from sparkden.shared.minio import save_objects
from sqlalchemy import delete, func, select, update
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession


class KnowledgeDataSourceService(BaseService):
    async def list_data_sources(
        self, collection_id: str, *, limit: int = 30, offset: int = 0
    ) -> OffsetPagination[KnowledgeDataSource]:
        async with self.db_session_maker.begin() as db_session:
            query = (
                select(
                    StorageDataSource,
                    func.count().over().label("total_count"),
                )
                .where(StorageDataSource.collection_id == collection_id)
                .order_by(StorageDataSource.created_at.desc())
                .offset(offset)
                .limit(limit)
            )
            result = (await db_session.execute(query)).all()
            data_sources = [KnowledgeDataSource.from_storage(row[0]) for row in result]
            total = result[0][1] if result else 0
            return OffsetPagination(
                items=data_sources,
                total=total,
                limit=limit,
                offset=offset,
            )

    async def get_data_source(self, data_source_id: str) -> KnowledgeDataSource | None:
        async with self.db_session_maker.begin() as db_session:
            data_source = await db_session.get(StorageDataSource, data_source_id)
            if data_source:
                return KnowledgeDataSource.from_storage(data_source)
            return None

    async def list_data_source_chunks(
        self,
        collection_id: str,
        data_source_id: str,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> OffsetPagination[DataChunk]:
        filter = Filter(
            must=[
                FieldCondition(
                    key="data_source_id",
                    match=MatchValue(value=data_source_id),
                ),
            ]
        )

        vector_store = VectorStore(
            collection_name=collection_id,
        )

        chunks = await vector_store.filter_chunks(
            filter,
            limit,
            offset,
            OrderBy(field="sequence_in_data_source", desc=False),
        )

        items = [
            DataChunk(
                id=chunk.id,
                content=chunk.content,
                metadata=chunk.metadata,
            )
            for chunk in chunks
        ]

        return OffsetPagination(
            items=items,
            total=await vector_store.count_chunks(filter),
            limit=limit,
            offset=offset,
        )

    async def add_data_source(
        self, data_source: KnowledgeDataSourceCreate, auto_load: bool = True
    ) -> tuple[KnowledgeDataSource, bool, str | None]:
        """
        Adds a new data source.
        For file uploads, it dispatches an async job to process the data.

        Returns:
            A tuple of (KnowledgeDataSource, created_newly, job_id)
        """

        from sparkden.queued_job.data_source_job import data_source_job

        data_source_creator = knowledge_collections.get_data_source_creator(
            data_source.creator_id
        )
        if not data_source_creator:
            raise ValueError("Data source creator not found")

        file: FileObject | None = None
        if data_source_creator.type == DataSourceCreatorType.UPLOAD:
            file = data_source.pop_extra_info("file")
            if not file:
                raise ValueError("File not found")
            file = cast(FileObject, file)

        async with self.db_session_maker.begin() as db_session:
            # prevent duplicate file data source
            if file:
                existing_data_source = await get_data_source_by_file_hash(
                    data_source.collection_id, file.hash, db_session
                )
                if existing_data_source:
                    return existing_data_source, False, None

                data_source.set_extra_info("file_hash", file.hash)

            new_data_source = await create_data_source(data_source, db_session)

        if file:
            save_objects(
                bucket_name=new_data_source.collection_id,
                objects=[
                    file.model_copy(
                        update={"name": new_data_source.file_object_name},
                        deep=True,
                    )
                ],
            )

        if auto_load:
            # Dispatch async job after transaction commits
            message = data_source_job.send(
                data_source_id=new_data_source.id,
                user_id=self.user_id,
            )
            job_id = message.message_id
            updated_data_source = await self.update_data_source(
                new_data_source.id,
                {
                    "status": DataSourceStatus.PROCESSING,
                    "extra_info": {"job_id": job_id},
                },
            )
            return updated_data_source, True, job_id

        return new_data_source, True, None

    async def delete_data_source(self, data_source_id: str) -> None:
        async with self.db_session_maker.begin() as db_session:
            data_source = await db_session.scalar(
                delete(StorageDataSource)
                .where(
                    StorageDataSource.id == data_source_id,
                )
                .returning(StorageDataSource)
            )
        if not data_source:
            return

        loader = DataLoader(
            data_source=KnowledgeDataSource.from_storage(data_source),
        )
        await loader.unload()

    async def refresh_data_source(self, data_source_id: str) -> str:
        from sparkden.queued_job.data_source_job import data_source_job

        data_source = await self.get_data_source(data_source_id)
        if not data_source:
            raise ValueError("Data source not found")

        message = data_source_job.send(
            data_source_id=data_source.id,
            user_id=self.user_id,
            reload=True,
        )
        job_id = message.message_id
        await self.update_data_source(
            data_source.id,
            {"status": DataSourceStatus.PROCESSING, "extra_info": {"job_id": job_id}},
        )
        return job_id

    async def update_data_source(
        self,
        data_source_id: str,
        update_attributes: dict[str, Any],
    ) -> KnowledgeDataSource:
        """Update the status for a data source"""
        data_source = await self.get_data_source(data_source_id)
        if not data_source:
            raise ValueError("Data source not found")

        if update_attributes.get("extra_info"):
            update_attributes["extra_info"] = (
                data_source.extra_info or {}
            ) | update_attributes["extra_info"]

        async with self.db_session_maker.begin() as db_session:
            result = await db_session.scalar(
                update(StorageDataSource)
                .where(StorageDataSource.id == data_source_id)
                .values(update_attributes)
                .returning(StorageDataSource)
            )
            if not result:
                raise ValueError("Data source update failed")
            return KnowledgeDataSource.from_storage(result)


async def create_data_source(
    data_source: KnowledgeDataSourceCreate,
    db_session: AsyncSession,
) -> KnowledgeDataSource:
    data_source_attributes = {
        **data_source.model_dump(exclude_none=True),
    }
    data_source_id = await db_session.scalar(
        insert(StorageDataSource)
        .values(data_source_attributes)
        .on_conflict_do_update(
            index_elements=[StorageDataSource.id],
            set_=data_source_attributes,
        )
        .returning(StorageDataSource.id)
    )
    if not data_source_id:
        raise Exception("Failed to create data_source")
    if not data_source_id:
        raise Exception("Failed to create data_source")
    data_source_attributes["id"] = str(data_source_id)
    return KnowledgeDataSource(**data_source_attributes)


async def get_data_source_by_file_hash(
    collection_id: str,
    file_hash: str,
    db_session: AsyncSession,
) -> KnowledgeDataSource | None:
    query = select(StorageDataSource).where(
        StorageDataSource.collection_id == collection_id,
        StorageDataSource.extra_info["file_hash"].astext == file_hash,
    )
    data_source = await db_session.scalar(query)
    if data_source:
        return KnowledgeDataSource.from_storage(data_source)
    return None
