import hashlib
from enum import StrEnum
from functools import cached_property
from typing import Any, Sequence

from pydantic import Field
from sparkden.db.schema import (
    DataSourceStatus,
)
from sparkden.db.schema import KnowledgeDataSource as StorageDataSource
from sparkden.knowledge.data_parsers.base import (
    BaseDataParser,
)
from sparkden.knowledge.data_splitters.base import (
    BaseDataSplitter,
)
from sparkden.models.shared import BaseModel, ExtraInfoMixin


class VectorDistance(StrEnum):
    COSINE = "Cosine"
    EUCLID = "Euclid"
    DOT = "Dot"
    MANHATTAN = "Manhattan"


class RetrievalMode(StrEnum):
    DENSE = "dense"
    SPARSE = "sparse"
    HYBRID = "hybrid"


class DataSourceCreatorType(StrEnum):
    UPLOAD = "upload"
    CUSTOM = "custom"


class DataSourceCreator[DataType: BaseModel](ExtraInfoMixin, BaseModel):
    id: str
    type: DataSourceCreatorType = DataSourceCreatorType.UPLOAD
    data_parser: BaseDataParser[DataType] | None = Field(default=None, exclude=True)
    data_splitter: BaseDataSplitter | None = Field(default=None, exclude=True)


class KnowledgeCollection(BaseModel):
    id: str
    vector_dimensions: int = 1024
    vector_distance: VectorDistance = VectorDistance.COSINE
    retrieval_mode: RetrievalMode = RetrievalMode.HYBRID
    data_source_creators: Sequence[DataSourceCreator] | None = None


class KnowledgeDataSource(ExtraInfoMixin, BaseModel):
    id: str
    creator_id: str
    name: str
    collection_id: str
    status: DataSourceStatus

    @property
    def file_object_name(self) -> str:
        return f"{self.id}/original"

    @classmethod
    def from_storage(cls, data_source: StorageDataSource) -> "KnowledgeDataSource":
        return cls(
            id=str(data_source.id),
            creator_id=data_source.creator_id,
            name=data_source.name,
            status=data_source.status,
            extra_info=data_source.extra_info,
            collection_id=data_source.collection_id,
        )


class KnowledgeDataSourceCreate(KnowledgeDataSource):
    id: str | None = None
    status: DataSourceStatus = DataSourceStatus.NOT_LOADED


class FileObject(BaseModel):
    name: str
    content: bytes
    content_type: str

    @cached_property
    def hash(self) -> str:
        return hashlib.sha256(self.content).hexdigest()


class ParseResultType(StrEnum):
    TEXT = "text"
    MARKDOWN = "markdown"
    TABLE = "table"


class FileExtractConfig(BaseModel):
    object_base_name: str
    parsed_object_name: str
    bucket_name: str


class ParseResult(BaseModel):
    data: str | list
    data_type: ParseResultType
    extracted_files: list[FileObject] = []


class DataChunk(BaseModel):
    id: str
    content: str
    metadata: dict[str, Any]


class ScoredDataChunk(DataChunk):
    score: float
    retrieval_mode: RetrievalMode
