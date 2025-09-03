"""
Configures the job queue broker and Redis clients
"""

import os

import dramatiq
import redis
import redis.asyncio as aioredis
from dramatiq.brokers.redis import RedisBroker
from dramatiq.middleware import AsyncIO
from dramatiq.results import Results
from dramatiq.results.backends.redis import RedisBackend


def get_redis_url() -> str:
    """Get Redis URL."""
    return os.getenv("REDIS_URL", "redis://localhost:6379")


def create_redis_client() -> redis.Redis:
    """Create synchronous Redis client (for Dramatiq)."""
    return redis.from_url(get_redis_url())


def create_redis_async_client() -> aioredis.Redis:
    """Create async Redis client (for progress notifications and SSE)."""
    return aioredis.from_url(get_redis_url())


def setup_job_queue_broker() -> RedisBroker:
    """Setup job queue broker."""
    redis_url = get_redis_url()

    broker = RedisBroker(url=redis_url)

    # Add async middleware for async job execution
    broker.add_middleware(AsyncIO())

    # Add result backend
    result_backend = RedisBackend(url=redis_url)
    broker.add_middleware(Results(backend=result_backend))

    dramatiq.set_broker(broker)
    return broker


# Global broker instance (lazy init)
_broker = None


def get_job_queue_broker() -> RedisBroker:
    """Get job queue broker (singleton)."""
    global _broker
    if _broker is None:
        _broker = setup_job_queue_broker()
    return _broker


def reset_broker():
    """Reset broker (for testing)."""
    global _broker
    _broker = None
