from litestar import get
from litestar.types import Scope
from litestar.utils.scope.state import ScopeState


@get("/csrf-token", exclude_from_auth=True)
async def csrf_token(scope: Scope) -> str | None:
    token = ScopeState.from_scope(scope).csrf_token
    if not isinstance(token, str):
        return None
    return token
