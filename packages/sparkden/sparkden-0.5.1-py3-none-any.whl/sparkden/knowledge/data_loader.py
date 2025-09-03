import json
from abc import ABC
from typing import AsyncGenerator

from qdrant_client.http.models import (
    FieldCondition,
    Filter,
    MatchValue,
)
from sparkden.knowledge.data_parsers.file_parser import FileParser
from sparkden.knowledge.data_splitters.default_splitter import DefaultSplitter
from sparkden.models.knowledge import (
    DataChunk,
    DataSourceCreatorType,
    FileExtractConfig,
    KnowledgeDataSource,
    ParseResult,
    ParseResultType,
    RetrievalMode,
)
from sparkden.shared.minio import (
    delete_objects,
    get_minio_client,
    get_object,
    object_exists,
    save_objects,
)

from .embeddings import Embeddings
from .vector_store import VectorStore


class DataLoader(ABC):
    def __init__(
        self,
        data_source: KnowledgeDataSource,
        vector_dimensions: int = 1024,
        retrieval_mode: RetrievalMode = RetrievalMode.DENSE,
    ):
        from sparkden.knowledge.registry import knowledge_collections

        self.data_source = data_source
        self.vector_dimensions = vector_dimensions
        self.retrieval_mode = retrieval_mode

        data_source_creator = knowledge_collections.get_data_source_creator(
            self.data_source.creator_id
        )
        if not data_source_creator:
            raise ValueError("Data source creator not found")

        self.data_source_creator = data_source_creator

        data_parser = (
            data_source_creator.data_parser
            if data_source_creator.data_parser
            else FileParser()
            if self.data_source_creator.type == DataSourceCreatorType.UPLOAD
            else None
        )

        if not data_parser:
            raise ValueError("Data parser should be provided in data source creator.")

        self.data_parser = data_parser

        self.data_splitter = (
            data_source_creator.data_splitter
            if data_source_creator.data_splitter
            else DefaultSplitter()
        )

    @property
    def bucket_name(self) -> str:
        return self.data_source.collection_id

    @property
    def vector_collection_name(self) -> str:
        return self.data_source.collection_id

    async def parse(self) -> ParseResult:
        object_base_name = self.data_source.id
        parsed_object_name = f"{object_base_name}/parsed"

        # If the data source is already parsed, return the parsed result
        if object_exists(self.bucket_name, parsed_object_name):
            parsed_file = get_object(self.bucket_name, parsed_object_name)
            if not parsed_file:
                raise ValueError(
                    f"Parsed file not found: bucket={self.bucket_name}, object_name={parsed_object_name}"
                )

            if parsed_file.content_type == "text/plain":
                return ParseResult(
                    data=parsed_file.content.decode("utf-8"),
                    data_type=ParseResultType.TEXT,
                )
            elif parsed_file.content_type == "text/markdown":
                return ParseResult(
                    data=parsed_file.content.decode("utf-8"),
                    data_type=ParseResultType.MARKDOWN,
                )
            elif parsed_file.content_type == "application/json":
                return ParseResult(
                    data=json.loads(parsed_file.content.decode("utf-8")),
                    data_type=ParseResultType.TABLE,
                )
            else:
                raise ValueError(
                    f"Unsupported parsed file type: {parsed_file.content_type}"
                )

        if isinstance(self.data_parser, FileParser):
            file = get_object(self.bucket_name, self.data_source.file_object_name)
            if not file:
                raise ValueError(
                    f"File not found: bucket={self.bucket_name}, object_name={self.data_source.file_object_name}"
                )
            input_data = {"file": file}
        else:
            input_data = self.data_source.extra_info

            if not input_data:
                raise ValueError("Data source extra info is required")

        parse_result = await self.data_parser.parse(
            input_data,
            FileExtractConfig(
                object_base_name=object_base_name,
                parsed_object_name=parsed_object_name,
                bucket_name=self.bucket_name,
            ),
        )

        save_objects(self.bucket_name, parse_result.extracted_files)
        return parse_result

    async def load(self, reload: bool = False) -> AsyncGenerator[str, None]:
        if reload:
            yield "unloading"
            await self.unload()

        yield "parsing"
        parse_result = await self.parse()

        yield "splitting"
        chunks = await self.data_splitter.split(parse_result)

        for index, chunk in enumerate(chunks):
            chunk.metadata.update(
                {
                    "sequence_in_data_source": index + 1,
                    "data_source_id": self.data_source.id,
                }
            )

        yield "adding_chunks"
        await self._add_to_vector_store(chunks)

    async def unload(self) -> None:
        minio_client = get_minio_client()
        objects_to_delete = minio_client.list_objects(
            self.data_source.collection_id, prefix=self.data_source.id, recursive=True
        )

        delete_objects(
            self.bucket_name,
            [
                object.object_name
                for object in objects_to_delete
                if object.object_name
                and object.object_name != self.data_source.file_object_name
            ],
        )

        await self._delete_from_vector_store()

    async def reload(self) -> AsyncGenerator[str, None]:
        async for progress in self.load(reload=True):
            yield progress

    async def _add_to_vector_store(self, chunks: list[DataChunk]) -> None:
        embeddings = Embeddings(dimensions=self.vector_dimensions)
        vector_store = VectorStore(
            collection_name=self.vector_collection_name,
            retrieval_mode=self.retrieval_mode,
        )

        await vector_store.add_chunks(chunks, embeddings=embeddings)

    async def _delete_from_vector_store(self) -> None:
        vector_store = VectorStore(
            collection_name=self.vector_collection_name,
        )

        filter = Filter(
            must=[
                FieldCondition(
                    key="data_source_id",
                    match=MatchValue(value=self.data_source.id),
                ),
            ]
        )

        await vector_store.delete_chunks(filter)
