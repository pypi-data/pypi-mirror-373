import json
from typing import Annotated

from litestar import Controller, Request, delete, get, post
from litestar.connection import ASGIConnection
from litestar.datastructures import UploadFile
from litestar.di import Provide
from litestar.enums import RequestEncodingType
from litestar.exceptions import (
    NotAuthorizedException,
    NotFoundException,
    ValidationException,
)
from litestar.handlers.base import BaseRouteHandler
from litestar.params import Body
from litestar.plugins.pydantic import PydanticDTO
from sparkden.knowledge.registry import knowledge_collections
from sparkden.knowledge.vector_store.base import FieldCondition, Filter, MatchAny
from sparkden.models.shared import BaseModel, OffsetPagination
from sparkden.services.knowledge import KnowledgeService
from sparkden.shared.utils import dto_config

from ..models.knowledge import (
    DataChunk,
    DataSourceCreatorType,
    FileObject,
    KnowledgeCollection,
    KnowledgeDataSource,
    KnowledgeDataSourceCreate,
    RetrievalMode,
    ScoredDataChunk,
)


class CollectionsResponse(BaseModel):
    collections: list[KnowledgeCollection]


class CreateDataSourceParams(BaseModel):
    creator_id: str
    extra_info: str | None = None
    file: UploadFile | None = None


class CreateDataSourceResponse(BaseModel):
    data_source: KnowledgeDataSource
    created: bool
    job_id: str | None = None


class RefreshDataSourceResponse(BaseModel):
    job_id: str


class SearchCollectionResponse(BaseModel):
    chunks: list[ScoredDataChunk]


CollectionsResponseDTO = PydanticDTO[
    Annotated[
        CollectionsResponse,
        dto_config(),
    ]
]

CollectionResponseDTO = PydanticDTO[
    Annotated[
        KnowledgeCollection,
        dto_config(),
    ]
]

ListDataSourcesResponseDTO = PydanticDTO[
    Annotated[
        OffsetPagination[KnowledgeDataSource],
        dto_config(),
    ]
]

CreateDataSourceResponseDTO = PydanticDTO[
    Annotated[
        CreateDataSourceResponse,
        dto_config(),
    ]
]

RefreshDataSourceResponseDTO = PydanticDTO[
    Annotated[
        RefreshDataSourceResponse,
        dto_config(),
    ]
]

CreateDataSourceParamsDTO = PydanticDTO[
    Annotated[
        CreateDataSourceParams,
        dto_config(),
    ]
]

ListDataChunksResponseDTO = PydanticDTO[
    Annotated[
        OffsetPagination[DataChunk],
        dto_config(),
    ]
]

SearchResultsResponseDTO = PydanticDTO[
    Annotated[
        SearchCollectionResponse,
        dto_config(),
    ]
]


def get_knowledge_service(request: Request) -> KnowledgeService:
    return KnowledgeService(
        user_id=str(request.user.id),
    )


def admin_user_guard(connection: ASGIConnection, _: BaseRouteHandler) -> None:
    if not connection.user.is_admin:
        raise NotAuthorizedException()


class KnowledgeController(Controller):
    path = "/knowledge"
    guards = [admin_user_guard]
    dependencies = {
        "knowledge_service": Provide(get_knowledge_service, sync_to_thread=True),
    }
    request_max_body_size = 50 * 1024 * 1024  # 50MB

    @get(
        "/collections",
        return_dto=CollectionsResponseDTO,
    )
    async def list_collections(
        self, knowledge_service: KnowledgeService
    ) -> CollectionsResponse:
        collections = await knowledge_service.list_collections()
        return CollectionsResponse(collections=collections)

    @get(
        "/collections/{collection_id:str}",
        return_dto=CollectionResponseDTO,
    )
    async def get_collection(
        self, collection_id: str, knowledge_service: KnowledgeService
    ) -> KnowledgeCollection:
        collection = await knowledge_service.get_collection(collection_id=collection_id)
        if not collection:
            raise NotFoundException(status_code=404, detail="Collection not found")
        return collection

    @get(
        "/collections/{collection_id:str}/data-sources",
        return_dto=ListDataSourcesResponseDTO,
    )
    async def list_data_sources(
        self,
        collection_id: str,
        knowledge_service: KnowledgeService,
        limit: int = 30,
        offset: int = 0,
    ) -> OffsetPagination[KnowledgeDataSource]:
        return await knowledge_service.list_data_sources(
            collection_id=collection_id, limit=limit, offset=offset
        )

    @get(
        "/collections/{collection_id:str}/data-sources/{data_source_id:str}/chunks",
        return_dto=ListDataChunksResponseDTO,
    )
    async def list_data_source_chunks(
        self,
        collection_id: str,
        data_source_id: str,
        knowledge_service: KnowledgeService,
        limit: int = 20,
        offset: int = 0,
    ) -> OffsetPagination[DataChunk]:
        return await knowledge_service.list_data_source_chunks(
            collection_id,
            data_source_id,
            limit=limit,
            offset=offset,
        )

    @post(
        "/collections/{collection_id:str}/data-sources",
        return_dto=CreateDataSourceResponseDTO,
        dto=CreateDataSourceParamsDTO,
    )
    async def create_data_source(
        self,
        collection_id: str,
        knowledge_service: KnowledgeService,
        data: Annotated[
            CreateDataSourceParams, Body(media_type=RequestEncodingType.MULTI_PART)
        ],
    ) -> CreateDataSourceResponse:
        data_source_creator = knowledge_collections.get_data_source_creator(
            data.creator_id
        )
        if not data_source_creator:
            raise ValidationException(
                status_code=400, detail="Data source creator not found"
            )

        if data_source_creator.type == DataSourceCreatorType.UPLOAD:
            if not data.file:
                raise ValidationException(status_code=400, detail="File is required")
            accept = [
                mime.strip()
                for mime in data_source_creator.get_extra_info("accept", "").split(",")
            ]
            if not any(data.file.content_type.startswith(mime) for mime in accept):
                raise ValidationException(
                    status_code=400,
                    detail=f"File must be one of the following types: {', '.join(accept)}",
                )
            file_content = await data.file.read()
            data_source = KnowledgeDataSourceCreate(
                creator_id=data_source_creator.id,
                name=data.file.filename,
                collection_id=collection_id,
                extra_info={
                    **(data_source_creator.extra_info or {}),
                    **(json.loads(data.extra_info) if data.extra_info else {}),
                    "file": FileObject(
                        name=data.file.filename,
                        content=file_content,
                        content_type=data.file.content_type,
                    ),
                },
            )
            data_source, created, job_id = await knowledge_service.add_data_source(
                data_source=data_source
            )
            return CreateDataSourceResponse(
                data_source=data_source, created=created, job_id=job_id
            )
        else:
            # TODO: create remote data source
            raise NotImplementedError("Not implemented")

    @delete("/collections/{collection_id:str}/data-sources/{data_source_id:str}")
    async def delete_data_source(
        self, data_source_id: str, knowledge_service: KnowledgeService
    ) -> None:
        await knowledge_service.delete_data_source(data_source_id)

    @post(
        "/collections/{collection_id:str}/data-sources/{data_source_id:str}/refresh",
        return_dto=RefreshDataSourceResponseDTO,
    )
    async def refresh_data_source(
        self, data_source_id: str, knowledge_service: KnowledgeService
    ) -> RefreshDataSourceResponse:
        job_id = await knowledge_service.refresh_data_source(data_source_id)
        return RefreshDataSourceResponse(job_id=job_id)

    @get(
        "/collections/{collection_id:str}/search",
        return_dto=SearchResultsResponseDTO,
    )
    async def search_collection(
        self,
        collection_id: str,
        knowledge_service: KnowledgeService,
        search_query: str,
        data_source_ids: list[str] | None = None,
        k: int = 5,
        retrieval_mode: str | None = "dense",
    ) -> SearchCollectionResponse:
        filter = (
            Filter(
                must=[
                    FieldCondition(
                        key="data_source_id",
                        match=MatchAny(any=data_source_ids),
                    ),
                ],
            )
            if data_source_ids
            else None
        )
        chunks = await knowledge_service.search_collection(
            collection_id=collection_id,
            query=search_query,
            filter=filter,
            k=k,
            retrieval_mode=RetrievalMode(retrieval_mode),
        )
        return SearchCollectionResponse(chunks=chunks)
