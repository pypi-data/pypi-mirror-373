from abc import ABC, abstractmethod
from enum import StrEnum
from itertools import islice
from typing import Any, Generator, Literal

from qdrant_client import models

from sparkden.models.knowledge import DataChunk, RetrievalMode, ScoredDataChunk
from sparkden.models.shared import BaseModel, OrderBy

from ..embeddings.base import BaseEmbeddings, DenseOutput, SparseOutput

Distance = models.Distance
VectorParams = models.VectorParams
SparseVectorParams = models.SparseVectorParams
Filter = models.Filter
MatchValue = models.MatchValue
MatchAny = models.MatchAny
FieldCondition = models.FieldCondition
SparseVector = models.SparseVector


class Field(BaseModel):
    name: str
    type: Literal[
        "string", "integer", "float", "bool", "text", "datetime", "uuid", "geo"
    ]
    default: Any = None


class SearchMode(StrEnum):
    DENSE = "dense"
    SPARSE = "sparse"
    HYBRID = "hybrid"


class BaseVectorStore(ABC):
    VECTOR_NAME = "vector"
    SPARSE_VECTOR_NAME = "sparse_vector"
    CONTENT_PAYLOAD_KEY = "content"

    def __init__(
        self,
        collection_name: str,
        retrieval_mode: RetrievalMode = RetrievalMode.DENSE,
        hybrid_dense_ratio: float = 0.6,
    ):
        self.collection_name = collection_name
        self.retrieval_mode = retrieval_mode
        self.hybrid_dense_ratio = hybrid_dense_ratio

    @classmethod
    @abstractmethod
    async def create_collection(
        cls,
        collection_name: str,
        vector_name: str | None = None,
        vector_params: VectorParams | None = None,
        sparse_vector_name: str | None = None,
        sparse_vector_params: SparseVectorParams | None = None,
        payload_fields: list[Field] | None = None,
        recreate_if_exists: bool = False,
    ) -> None:
        pass

    @classmethod
    @abstractmethod
    async def create_index(cls, collection_name: str, field: Field) -> None:
        pass

    async def add_chunks(
        self,
        chunks: list[DataChunk],
        *,
        embeddings: BaseEmbeddings,
        batch_size: int = 10,
    ) -> list[str]:
        added_ids = []
        for vectors, sparse_vectors, payloads, ids in self._generate_batches(
            chunks, embeddings, batch_size
        ):
            await self.add_vectors(vectors, sparse_vectors, payloads, ids)
            added_ids.extend(ids)

        return added_ids

    def _generate_batches(
        self,
        chunks: list[DataChunk],
        embeddings: BaseEmbeddings,
        batch_size: int = 10,
    ) -> Generator[
        tuple[DenseOutput | None, SparseOutput | None, list[dict], list[str]],
        None,
        None,
    ]:
        texts = iter([chunk.content for chunk in chunks])
        metadatas = iter([chunk.metadata for chunk in chunks])
        ids = iter([chunk.id for chunk in chunks])

        while batch_texts := list(islice(texts, batch_size)):
            batch_metadatas = list(islice(metadatas, batch_size))
            batch_ids = list(islice(ids, batch_size))

            vectors = None
            sparse_vectors = None
            if self.retrieval_mode == RetrievalMode.DENSE:
                vectors = embeddings.embed_documents(batch_texts, self.retrieval_mode)
            elif self.retrieval_mode == RetrievalMode.SPARSE:
                sparse_vectors = embeddings.embed_documents(
                    batch_texts, self.retrieval_mode
                )
            elif self.retrieval_mode == RetrievalMode.HYBRID:
                vectors, sparse_vectors = embeddings.embed_documents(
                    batch_texts, self.retrieval_mode
                )

            payloads = [
                {**metadata, self.CONTENT_PAYLOAD_KEY: text}
                for text, metadata in zip(batch_texts, batch_metadatas)
            ]

            yield vectors, sparse_vectors, payloads, batch_ids

    @abstractmethod
    async def add_vectors(
        self,
        vectors: DenseOutput | None,
        sparse_vectors: SparseOutput | None,
        payloads: list[dict],
        ids: list[str] | None = None,
    ) -> None:
        pass

    @abstractmethod
    async def delete_chunks(self, chunk_selector: list[str] | Filter) -> None:
        pass

    @abstractmethod
    async def count_chunks(self, filter: Filter) -> int:
        pass

    @abstractmethod
    async def filter_chunks(
        self,
        filter: Filter,
        limit: int = 20,
        offset: int = 0,
        order_by: OrderBy | None = None,
    ) -> list[ScoredDataChunk]:
        pass
