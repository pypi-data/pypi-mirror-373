import redis as redis
import redis.asyncio as async_redis

from .utils import getenv

_async_redis_client: async_redis.Redis | None = None
_redis_client: redis.Redis | None = None


def get_redis_client() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(
            getenv("REDIS_URL"), decode_responses=False
        )
    return _redis_client


def get_async_redis_client() -> async_redis.Redis:
    global _async_redis_client
    if _async_redis_client is None:
        _async_redis_client = async_redis.Redis.from_url(getenv("REDIS_URL"))
    return _async_redis_client
