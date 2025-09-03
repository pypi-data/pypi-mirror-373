from sparkden.knowledge.vector_store import (
    Distance,
    Field,
    SparseVectorParams,
    VectorParams,
    VectorStore,
)
from sparkden.models.knowledge import DataSourceCreator, KnowledgeCollection
from sparkden.shared.minio import get_minio_client


class KnowledgeCollectionRegistry:
    """Knowledge collection registry for managing registered knowledge collections."""

    def __init__(self, collections: list[KnowledgeCollection] = []):
        """Initialize the knowledge collection registry."""
        self._collections: dict[str, KnowledgeCollection] = {
            collection.id: collection for collection in collections
        }

    def register(
        self,
        collection: KnowledgeCollection,
    ) -> KnowledgeCollection:
        """
        Register a new knowledge collection.

        Args:
            collection: The knowledge collection to register

        Returns:
            The registered KnowledgeCollection instance

        Raises:
            ValueError: If a collection with the same ID is already registered
        """
        if collection.id in self._collections:
            raise ValueError(
                f"Knowledge collection with ID '{collection.id}' is already registered"
            )

        if collection.data_source_creators is None:
            collection.data_source_creators = [
                DataSourceCreator(
                    id="file_upload",
                    extra_info={"accept": "application/pdf,text/markdown,text/plain"},
                )
            ]

        self._collections[collection.id] = collection
        return collection

    def get_collection(self, id: str) -> KnowledgeCollection | None:
        """
        Get a knowledge collection by ID.

        Args:
            id: The collection ID

        Returns:
            The collection if found, None otherwise
        """
        return self._collections.get(id)

    def get_collections(self) -> list[KnowledgeCollection]:
        """
        Get all registered knowledge collections.

        Returns:
            List of collections sorted by ID for consistent ordering
        """
        return sorted(self._collections.values(), key=lambda c: c.id)

    def unregister(self, id: str) -> bool:
        """
        Unregister a knowledge collection by ID.

        Args:
            id: The collection ID

        Returns:
            True if the collection was found and removed, False otherwise
        """
        if id in self._collections:
            del self._collections[id]
            return True
        return False

    def is_registered(self, id: str) -> bool:
        """
        Check if a knowledge collection is registered.

        Args:
            id: The collection ID

        Returns:
            True if the collection is registered, False otherwise
        """
        return id in self._collections

    def clear(self) -> None:
        """Clear all registered knowledge collections."""
        self._collections.clear()

    def get_data_source_creator(self, creator_id: str) -> DataSourceCreator | None:
        """
        Get a data source creator by ID from all registered collections.

        Args:
            creator_id: The creator ID

        Returns:
            The data source creator if found, None otherwise
        """
        for collection in self.get_collections():
            if collection.data_source_creators:
                for creator in collection.data_source_creators:
                    if creator.id == creator_id:
                        return creator
        return None

    async def create_all(self) -> None:
        for collection in self.get_collections():
            await create_collection(collection)


async def create_collection(
    knowledge_collection: KnowledgeCollection,
) -> None:
    try:
        minio_client = get_minio_client()
        if not minio_client.bucket_exists(knowledge_collection.id):
            minio_client.make_bucket(knowledge_collection.id)
            print(f"Created MinIO bucket: {knowledge_collection.id}")
    except Exception as e:
        print(f"Unexpected error initializing MinIO bucket: {e}")
        raise

    try:
        created = await VectorStore.create_collection(
            knowledge_collection.id,
            vector_params=VectorParams(
                size=knowledge_collection.vector_dimensions,
                distance=Distance(knowledge_collection.vector_distance),
            ),
            sparse_vector_params=SparseVectorParams(),
        )
        if created:
            print(f"Vector store collection created: {knowledge_collection.id}")

            await VectorStore.create_index(
                knowledge_collection.id,
                Field(name="sequence_in_data_source", type="integer"),
            )
    except Exception as e:
        print(f"Unexpected error initializing vector store collection: {e}")
        raise


knowledge_collections = KnowledgeCollectionRegistry()
knowledge_collection_registry = knowledge_collections
