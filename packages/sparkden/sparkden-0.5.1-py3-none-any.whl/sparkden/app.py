import os
from typing import TYPE_CHECKING

from dotenv import load_dotenv
from litestar import Litestar

if TYPE_CHECKING:
    from .models.assistant import Assistant
    from .models.knowledge import KnowledgeCollection

# env variables auto loaded in docker compose
if os.getenv("REDIS_URL") is None:
    load_dotenv()


def create_app(
    assistants: "list[Assistant]" = [],
    knowledge_collections: "list[KnowledgeCollection]" = [],
) -> Litestar:
    import dramatiq
    from litestar.config.compression import CompressionConfig
    from litestar.config.cors import CORSConfig
    from litestar.config.csrf import CSRFConfig
    from litestar.stores.redis import RedisStore

    from .assistants.registry import assistant_registry
    from .db.init import init_db
    from .knowledge.registry import knowledge_collection_registry
    from .routes.assistants import AssistantController
    from .routes.files import FilesController
    from .routes.knowledge import KnowledgeController
    from .routes.queued_jobs import QueuedJobController
    from .routes.security.auth import session_auth, session_backend_config
    from .routes.security.csrf import csrf_token
    from .routes.tasks import TaskController
    from .shared import getenv
    from .shared.pg import dispose_engine
    from .shared.redis import get_async_redis_client
    from .worker.broker import create_broker

    broker = create_broker()
    dramatiq.set_broker(broker)

    for assistant in assistants:
        assistant_registry.register(assistant)

    for knowledge_collection in knowledge_collections:
        knowledge_collection_registry.register(knowledge_collection)

    return Litestar(
        route_handlers=[
            csrf_token,
            AssistantController,
            TaskController,
            KnowledgeController,
            FilesController,
            QueuedJobController,
            *assistant_registry.get_api_routes(),
        ],
        stores={
            session_backend_config.store: RedisStore(
                redis=get_async_redis_client(),
                namespace="sessions",
                handle_client_shutdown=True,
            ),
        },
        lifespan=[*assistant_registry.get_callbacks("lifespan")],
        on_app_init=[
            session_auth.on_app_init,
            *assistant_registry.get_callbacks("on_app_init"),
        ],
        on_startup=[
            init_db,
            knowledge_collection_registry.create_all,
            *assistant_registry.get_callbacks("on_startup"),
        ],
        on_shutdown=[dispose_engine, *assistant_registry.get_callbacks("on_shutdown")],
        csrf_config=CSRFConfig(
            secret=getenv("CSRF_SECRET"),
        ),
        cors_config=CORSConfig(
            allow_origins=[url.strip() for url in getenv("CLIENT_URL", "*").split(",")],
            allow_credentials=True,
        ),
        compression_config=CompressionConfig(backend="gzip"),
        openapi_config=None,
        debug=getenv("DEBUG", "false") == "true",
    )
