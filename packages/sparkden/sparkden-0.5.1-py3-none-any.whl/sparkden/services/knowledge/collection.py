from sparkden.knowledge.embeddings import Embeddings
from sparkden.knowledge.registry import knowledge_collections
from sparkden.knowledge.vector_store import (
    Filter,
    VectorStore,
)
from sparkden.models.knowledge import (
    KnowledgeCollection,
    RetrievalMode,
    ScoredDataChunk,
)
from sparkden.services.base import BaseService


class KnowledgeCollectionService(BaseService):
    async def list_collections(self) -> list[KnowledgeCollection]:
        return knowledge_collections.get_collections()

    async def get_collection(self, collection_id: str) -> KnowledgeCollection | None:
        return knowledge_collections.get_collection(collection_id)

    async def search_collection(
        self,
        collection_id: str,
        query: str,
        filter: Filter | None = None,
        k: int = 5,
        retrieval_mode: RetrievalMode = RetrievalMode.HYBRID,
        score_threshold: float | None = None,
    ) -> list[ScoredDataChunk]:
        collection = knowledge_collections.get_collection(collection_id)
        if not collection:
            raise ValueError(f"Collection not found: {collection_id}")

        vector_store = VectorStore(
            collection_name=collection_id, retrieval_mode=retrieval_mode
        )

        embeddings = Embeddings(dimensions=collection.vector_dimensions)
        return await vector_store.search(query, embeddings, filter, k, score_threshold)
