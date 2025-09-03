import hashlib
from typing import Annotated, Any

from bcrypt import checkpw
from litestar import Controller, Request, delete, get, post
from litestar.connection import ASGIConnection
from litestar.exceptions import NotAuthorizedException
from litestar.middleware.authentication import AuthenticationResult
from litestar.middleware.session.server_side import (
    ServerSideSessionBackend,
    ServerSideSessionConfig,
)
from litestar.plugins.pydantic import PydanticDTO
from litestar.security.session_auth import SessionAuth, SessionAuthMiddleware
from sparkden.db.schema import ApiKey
from sparkden.db.schema import User as StorageUser
from sparkden.models.shared import BaseModel
from sparkden.models.user import User
from sparkden.shared.pg import get_session_maker
from sparkden.shared.utils import dto_config
from sqlalchemy import select


class Session(BaseModel):
    user: User


class SignInUser(BaseModel):
    username: str
    password: str


SignInUserDTO = PydanticDTO[Annotated[SignInUser, dto_config()]]
SessionDTO = PydanticDTO[Annotated[Session, dto_config()]]


class SessionController(Controller):
    path = "/sessions"

    @get("/", return_dto=SessionDTO)
    async def get_session(self, request: Request) -> Session:
        return Session(user=request.user)

    @post("/", dto=SignInUserDTO, return_dto=SessionDTO, exclude_from_auth=True)
    async def sign_in(self, data: SignInUser, request: Request) -> Session:
        async with get_session_maker().begin() as db_session:
            user = await db_session.scalar(
                select(StorageUser).where(StorageUser.username == data.username)
            )
            if not user or not user.password:
                raise NotAuthorizedException(
                    status_code=401, detail="Invalid username or password"
                )
            if not checkpw(data.password.encode(), user.password):
                raise NotAuthorizedException(
                    status_code=401, detail="Invalid username or password"
                )
            request.set_session({"user_id": user.id})
            return Session(user=User.from_storage(user))

    @delete("/", exclude_from_auth=True)
    async def sign_out(self, request: Request) -> None:
        request.clear_session()


async def retrieve_user_handler(
    session: dict[str, Any], connection: ASGIConnection
) -> User | None:
    async with get_session_maker().begin() as db_session:
        if user_id := session.get("user_id"):
            storage_user = await db_session.get(StorageUser, user_id)
        return User.from_storage(storage_user) if storage_user else None


class APIKeyAndSessionAuthMiddleware(SessionAuthMiddleware):
    async def authenticate_request(
        self, connection: ASGIConnection[Any, Any, Any, Any]
    ) -> AuthenticationResult:
        if api_key := connection.headers.get("X-API-KEY"):
            key_hash = hashlib.sha256(api_key.encode()).hexdigest()
            async with get_session_maker().begin() as db_session:
                storage_user = await db_session.scalar(
                    select(StorageUser).join(ApiKey).where(ApiKey.key_hash == key_hash)
                )
                if storage_user:
                    return AuthenticationResult(
                        user=User.from_storage(storage_user), auth=connection.session
                    )
        return await super().authenticate_request(connection)


session_backend_config = ServerSideSessionConfig()

session_auth = SessionAuth[User, ServerSideSessionBackend](
    retrieve_user_handler=retrieve_user_handler,
    session_backend_config=session_backend_config,
    authentication_middleware_class=APIKeyAndSessionAuthMiddleware,
    route_handlers=[
        SessionController,
    ],
)
