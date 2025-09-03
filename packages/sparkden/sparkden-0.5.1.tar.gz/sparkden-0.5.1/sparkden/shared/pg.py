from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from .utils import getenv

# 不立即创建 Engine，而是提供创建函数
_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def get_engine() -> AsyncEngine:
    DATABASE_URL = getenv("DATABASE_URL")
    global _engine
    if _engine is None:
        _engine = create_async_engine(DATABASE_URL)
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    global _session_maker
    if _session_maker is None:
        _session_maker = async_sessionmaker(get_engine(), expire_on_commit=False)
    return _session_maker


async def dispose_engine():
    global _engine
    if _engine is not None:
        await _engine.dispose()
        _engine = None
