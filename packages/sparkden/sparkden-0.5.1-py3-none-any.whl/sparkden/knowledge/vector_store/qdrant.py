from uuid import uuid4

from qdrant_client import AsyncQdrantClient
from qdrant_client import models as qdrant_models
from qdrant_client.conversions import common_types as qdrant_types

from sparkden.knowledge.embeddings.base import BaseEmbeddings
from sparkden.shared.utils import getenv

from .base import (
    BaseVectorStore,
    DataChunk,
    DenseOutput,
    Field,
    Filter,
    OrderBy,
    RetrievalMode,
    ScoredDataChunk,
    SparseOutput,
    SparseVector,
    SparseVectorParams,
    VectorParams,
)

_qdrant_client: AsyncQdrantClient | None = None


def get_qdrant_client() -> AsyncQdrantClient:
    global _qdrant_client
    if _qdrant_client is None:
        qdrant_url = getenv("QDRANT_URL")
        _qdrant_client = AsyncQdrantClient(url=qdrant_url)
    return _qdrant_client


class QdrantVectorStore(BaseVectorStore):
    def __init__(self, **kwargs):
        self.client = get_qdrant_client()
        super().__init__(**kwargs)

    @classmethod
    async def create_collection(
        cls,
        collection_name: str,
        *,
        vector_params: VectorParams | None = None,
        sparse_vector_params: SparseVectorParams | None = None,
        payload_fields: list[Field] | None = None,
        recreate_if_exists: bool = False,
    ) -> bool:
        qdrant_client = get_qdrant_client()
        if await qdrant_client.collection_exists(collection_name):
            if recreate_if_exists:
                await qdrant_client.delete_collection(collection_name)
            else:
                return False

        vectors_config = {cls.VECTOR_NAME: vector_params} if vector_params else None

        sparse_vectors_config = (
            {cls.SPARSE_VECTOR_NAME: sparse_vector_params}
            if sparse_vector_params
            else None
        )

        return await qdrant_client.create_collection(
            collection_name=collection_name,
            vectors_config=vectors_config,
            sparse_vectors_config=sparse_vectors_config,
        )

    @classmethod
    async def create_index(
        cls,
        collection_name: str,
        field: Field,
    ) -> None:
        if field.type == "integer":
            field_schema = qdrant_models.IntegerIndexParams(
                type=qdrant_models.IntegerIndexType.INTEGER,
                lookup=False,
                range=True,
            )
        else:
            field_schema = qdrant_models.PayloadSchemaType(field.type)

        qdrant_client = get_qdrant_client()
        await qdrant_client.create_payload_index(
            collection_name=collection_name,
            field_name=field.name,
            field_schema=field_schema,
        )

    async def add_vectors(
        self,
        vectors: DenseOutput | None,
        sparse_vectors: SparseOutput | None,
        payloads: list[dict],
        ids: list[str] | None = None,
    ) -> list[str]:
        if self.retrieval_mode == RetrievalMode.DENSE:
            if vectors is None:
                raise ValueError("Dense vectors are required for dense search mode")
        elif self.retrieval_mode == RetrievalMode.SPARSE:
            if sparse_vectors is None:
                raise ValueError("Sparse vectors are required for sparse search mode")
        elif self.retrieval_mode == RetrievalMode.HYBRID:
            if sparse_vectors is None or vectors is None:
                raise ValueError(
                    "Dense vectors and sparse vectors are required for hybrid search mode"
                )
        else:
            raise ValueError(f"Invalid retrieval mode: {self.retrieval_mode}")

        def get_vector_mapping(idx: int) -> qdrant_models.VectorStruct:
            if self.retrieval_mode == RetrievalMode.DENSE:
                assert vectors is not None
                return {self.VECTOR_NAME: vectors[idx]}
            elif self.retrieval_mode == RetrievalMode.SPARSE:
                assert sparse_vectors is not None
                return {
                    self.SPARSE_VECTOR_NAME: SparseVector(
                        indices=sparse_vectors[idx][0],
                        values=sparse_vectors[idx][1],
                    )
                }
            else:  # HYBRID
                assert vectors is not None and sparse_vectors is not None
                return {
                    self.VECTOR_NAME: vectors[idx],
                    self.SPARSE_VECTOR_NAME: SparseVector(
                        indices=sparse_vectors[idx][0],
                        values=sparse_vectors[idx][1],
                    ),
                }

        if ids is None:
            ids = [str(uuid4().hex) for _ in range(len(payloads))]

        points = [
            qdrant_models.PointStruct(
                id=point_id,
                vector=get_vector_mapping(idx),
                payload=payloads[idx],
            )
            for idx, point_id in enumerate(ids)
        ]
        await self.client.upsert(collection_name=self.collection_name, points=points)

        return ids

    async def count_chunks(self, filter: Filter) -> int:
        return (
            await self.client.count(
                collection_name=self.collection_name,
                count_filter=filter,
            )
        ).count

    async def delete_chunks(
        self, chunk_selector: list[qdrant_types.PointId] | Filter
    ) -> None:
        await self.client.delete(
            collection_name=self.collection_name,
            points_selector=chunk_selector,
        )

    async def filter_chunks(
        self,
        filter: Filter,
        limit: int = 20,
        offset: int = 0,
        order_by: OrderBy | None = None,
    ) -> list[DataChunk]:
        (points, _) = await self.client.scroll(
            collection_name=self.collection_name,
            scroll_filter=filter,
            limit=limit,
            order_by=qdrant_models.OrderBy(
                key=order_by.field,
                direction=qdrant_models.Direction.DESC
                if order_by.desc
                else qdrant_models.Direction.ASC,
                start_from=offset + 1,
            )
            if order_by
            else None,
        )

        return [
            DataChunk(
                id=str(point.id),
                content=point.payload.get("content", "") if point.payload else "",
                metadata={
                    k: v for k, v in (point.payload or {}).items() if k != "content"
                },
            )
            for point in points
        ]

    async def search(
        self,
        query: str,
        embeddings: BaseEmbeddings,
        query_filter: Filter | None = None,
        k: int = 5,
        score_threshold: float | None = None,
    ) -> list[ScoredDataChunk]:
        if self.retrieval_mode == RetrievalMode.DENSE:
            vector = embeddings.embed_query(query, RetrievalMode.DENSE)
            result = await self.client.query_points(
                collection_name=self.collection_name,
                query=vector,
                using=self.VECTOR_NAME,
                query_filter=query_filter,
                limit=k,
                score_threshold=score_threshold,
            )
        elif self.retrieval_mode == RetrievalMode.SPARSE:
            indices, values = embeddings.embed_query(query, RetrievalMode.SPARSE)
            result = await self.client.query_points(
                collection_name=self.collection_name,
                query=qdrant_models.SparseVector(indices=indices, values=values),
                using=self.SPARSE_VECTOR_NAME,
                query_filter=query_filter,
                limit=k,
                score_threshold=score_threshold,
            )
        elif self.retrieval_mode == RetrievalMode.HYBRID:
            vector, sparse_vector = embeddings.embed_query(query, RetrievalMode.HYBRID)
            result = await self.client.query_points(
                collection_name=self.collection_name,
                prefetch=[
                    qdrant_models.Prefetch(
                        query=vector,
                        filter=query_filter,
                        using=self.VECTOR_NAME,
                        limit=round(k * 2 * self.hybrid_dense_ratio),
                        score_threshold=score_threshold,
                    ),
                    qdrant_models.Prefetch(
                        query=qdrant_models.SparseVector(
                            indices=sparse_vector[0],
                            values=sparse_vector[1],
                        ),
                        filter=query_filter,
                        using=self.SPARSE_VECTOR_NAME,
                        limit=round(k * 2 * (1 - self.hybrid_dense_ratio)),
                    ),
                ],
                query=qdrant_models.FusionQuery(fusion=qdrant_models.Fusion.RRF),
                limit=k,
            )
        else:
            raise ValueError(f"Invalid retrieval mode: {self.retrieval_mode}")

        return [
            ScoredDataChunk(
                id=str(point.id),
                content=point.payload.get("content", "") if point.payload else "",
                metadata={
                    k: v for k, v in (point.payload or {}).items() if k != "content"
                },
                score=point.score,
                retrieval_mode=self.retrieval_mode,
            )
            for point in result.points
        ]
