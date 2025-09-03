import asyncio
import json
import uuid
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Optional, Set

from .config import create_redis_async_client


class JobProgressNotifier:
    """Job progress notifier with caching support."""

    def __init__(self):
        self.redis_client = create_redis_async_client()
        self.cache_ttl = 3600  # Cache for 1 hour after completion

    async def _cache_job_state(
        self, job_id: str, event_data: dict, is_completed: bool = False
    ) -> None:
        """Cache the latest job state in Redis.

        Args:
            job_id: Job ID
            event_data: Event data to cache
            is_completed: Whether this is a completion state
        """
        try:
            cache_key = f"job_state:{job_id}"

            # Add caching metadata
            cache_data = {
                **event_data,
                "cached_at": asyncio.get_event_loop().time(),
                "is_completed": is_completed,
            }

            # Set TTL based on completion status
            ttl = self.cache_ttl if is_completed else None

            await self.redis_client.set(cache_key, json.dumps(cache_data), ex=ttl)

        except Exception as e:
            print(f"Warning: Failed to cache job state for {job_id}: {e}")

    async def notify(
        self,
        job_id: str,
        progress_percent: int,
        message: str,
        user_id: str,
        database_id: Optional[str] = None,
        **extra_data: Any,
    ) -> None:
        """
        Send job progress notification to Redis Pub/Sub and cache the state.

        Args:
            job_id: Job ID
            progress_percent: Progress percentage (0-100, negative for error)
            message: Progress message
            user_id: User ID
            database_id: Database ID (optional)
            **extra_data: Extra data
        """
        if progress_percent < 0:
            status = "error"
        elif progress_percent >= 100:
            status = "completed"
        else:
            status = "running"

        event_data = {
            "job_id": job_id,
            "progress_percent": progress_percent,
            "message": message,
            "status": status,
            "user_id": user_id,
            "timestamp": str(uuid.uuid4()),
            **extra_data,
        }

        if database_id:
            event_data["database_id"] = database_id

        # Cache the job state for future retrieval
        is_completed = status in ["completed", "error"]
        await self._cache_job_state(job_id, event_data, is_completed)

        # Publish to Redis pub/sub channel
        channel = f"job_progress:{job_id}"
        await self.redis_client.publish(channel, json.dumps(event_data))

        # Logging
        print(
            f"[User: {user_id}] Job {job_id}"
            + (f" (DB: {database_id})" if database_id else "")
            + f": Progress {progress_percent}% - {message}"
        )

    async def get_cached_job_state(self, job_id: str) -> Optional[dict]:
        """Get cached job state from Redis.

        Args:
            job_id: Job ID to retrieve state for

        Returns:
            Cached job state dict or None if not found
        """
        try:
            cache_key = f"job_state:{job_id}"
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                return json.loads(cached_data)

            return None

        except Exception as e:
            print(f"Warning: Failed to retrieve cached job state for {job_id}: {e}")
            return None


class QueueJobStreamService:
    """Queue job stream service for managing job progress streams with caching support."""

    def __init__(self):
        self.redis_client = create_redis_async_client()
        self._active_streams: Set[str] = set()

    def get_active_streams(self) -> Set[str]:
        """Get currently active streams."""
        return self._active_streams.copy()

    @asynccontextmanager
    async def stream_manager(self, job_id: str):
        """Context manager for managing job progress streams."""
        self._active_streams.add(job_id)
        try:
            yield
        finally:
            self._active_streams.discard(job_id)

    async def get_cached_job_state(self, job_id: str) -> Optional[dict]:
        """Get cached job state from Redis.

        Args:
            job_id: Job ID to retrieve state for

        Returns:
            Cached job state dict or None if not found
        """
        try:
            cache_key = f"job_state:{job_id}"
            cached_data = await self.redis_client.get(cache_key)

            if cached_data:
                return json.loads(cached_data)

            return None

        except Exception as e:
            print(f"Warning: Failed to retrieve cached job state for {job_id}: {e}")
            return None

    async def stream_queued_job_progress(
        self, job_id: str
    ) -> AsyncGenerator[str, None]:
        """
        Stream job progress updates as Server-Sent Events (SSE).

        Args:
            job_id: Job ID to monitor

        Yields:
            SSE formatted strings with job progress updates
        """
        async with self.stream_manager(job_id):
            try:
                yield self._format_sse_event(
                    "connected",
                    {
                        "job_id": job_id,
                        "message": "Connected to queued job progress stream",
                    },
                )

                # Subscribe to Redis channel
                channel = f"job_progress:{job_id}"
                pubsub = self.redis_client.pubsub()
                await pubsub.subscribe(channel)

                try:
                    timeout = 300  # 5 minutes
                    start_time = asyncio.get_event_loop().time()

                    async for message in pubsub.listen():
                        if message["type"] == "message":
                            try:
                                data = json.loads(message["data"])

                                yield self._format_sse_event("progress", data)

                                if data.get("status") in ["completed", "error"]:
                                    yield self._format_sse_event(
                                        "finished",
                                        {
                                            "job_id": job_id,
                                            "final_status": data.get("status"),
                                        },
                                    )
                                    break

                            except json.JSONDecodeError:
                                continue

                        # Handle timeout
                        if asyncio.get_event_loop().time() - start_time > timeout:
                            yield self._format_sse_event(
                                "timeout", {"message": "Stream timeout after 5 minutes"}
                            )
                            break

                finally:
                    await pubsub.unsubscribe(channel)
                    await pubsub.aclose()

            except GeneratorExit:
                # TODO
                pass

            except Exception as e:
                yield self._format_sse_event(
                    "error", {"job_id": job_id, "error": str(e)}
                )

            finally:
                try:
                    yield self._format_sse_event(
                        "closed", {"job_id": job_id, "message": "Stream closed"}
                    )
                except GeneratorExit:
                    pass

    def _format_sse_event(self, event_type: str, data: dict) -> str:
        """Format SSE event string."""
        return f"event: {event_type}\ndata: {json.dumps(data)}\n\n"


job_progress_notifier = JobProgressNotifier()
queue_job_stream_service = QueueJobStreamService()


async def notify_job_progress(
    job_id: str,
    progress_percent: int,
    message: str,
    user_id: str,
    database_id: Optional[str] = None,
    **extra_data: Any,
) -> None:
    """
    Global function to send job progress notifications.

    Args:
        job_id: Job ID
        progress_percent: Progress percentage (0-100, negative for error)
        message: Progress message
        user_id: User ID
        database_id: Database ID (optional)
        **extra_data: Extra data
    """
    await job_progress_notifier.notify(
        job_id=job_id,
        progress_percent=progress_percent,
        message=message,
        user_id=user_id,
        database_id=database_id,
        **extra_data,
    )
