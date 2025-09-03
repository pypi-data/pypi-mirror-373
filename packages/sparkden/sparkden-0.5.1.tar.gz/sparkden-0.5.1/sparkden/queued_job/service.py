from datetime import datetime, timezone

import redis.asyncio as redis

from sparkden.shared.redis import get_async_redis_client

from .models import QueuedJob, QueuedJobStatus


class JobStatusService:
    _redis: redis.Redis
    _job_key_prefix = "queued_job:"
    _pubsub_channel_prefix = "queued_job_events:"

    def __init__(self, redis_instance: redis.Redis):
        self._redis = redis_instance

    def _get_job_key(self, job_id: str) -> str:
        return f"{self._job_key_prefix}{job_id}"

    def _get_pubsub_channel(self, job_id: str) -> str:
        return f"{self._pubsub_channel_prefix}{job_id}"

    async def get_job(self, job_id: str) -> QueuedJob | None:
        job_data = await self._redis.get(self._get_job_key(job_id))
        if not job_data:
            return None
        return QueuedJob.model_validate_json(job_data)

    async def create_job(self, job_id: str, user_id: str) -> QueuedJob:
        now = datetime.now(timezone.utc)
        job = QueuedJob(
            id=job_id,
            user_id=user_id,
            created_at=now,
            updated_at=now,
        )
        await self._update_and_publish(job)
        return job

    async def update_job_progress(
        self,
        job_id: str,
        progress: int,
        message: str | None = None,
        custom_status: str | None = None,
    ) -> QueuedJob:
        job = await self.get_job(job_id)
        if not job:
            raise ValueError(f"Job with id {job_id} not found")

        job.progress = progress
        if custom_status:
            job.custom_status = custom_status

        # In a real scenario, you might want to store the message somewhere,
        # but for now we'll just publish it. We'll add it to the model if needed.

        await self._update_and_publish(job)
        return job

    async def mark_job_as_running(
        self, job_id: str, custom_status: str | None = None
    ) -> QueuedJob:
        return await self._set_job_status(
            job_id, QueuedJobStatus.RUNNING, custom_status=custom_status
        )

    async def mark_job_as_success(self, job_id: str, result: dict) -> QueuedJob:
        return await self._set_job_status(
            job_id, QueuedJobStatus.SUCCESS, result=result
        )

    async def mark_job_as_failure(self, job_id: str, error: str) -> QueuedJob:
        return await self._set_job_status(job_id, QueuedJobStatus.FAILURE, error=error)

    async def _set_job_status(
        self,
        job_id: str,
        status: QueuedJobStatus,
        result: dict | None = None,
        error: str | None = None,
        custom_status: str | None = None,
    ) -> QueuedJob:
        job = await self.get_job(job_id)
        if not job:
            raise ValueError(f"Job with id {job_id} not found")

        job.status = status
        job.result = result
        job.error = error
        if custom_status:
            job.custom_status = custom_status

        if status in [QueuedJobStatus.SUCCESS, QueuedJobStatus.FAILURE]:
            job.progress = 100

        await self._update_and_publish(job)
        return job

    async def _update_and_publish(self, job: QueuedJob):
        job.updated_at = datetime.now(timezone.utc)
        job_json = job.model_dump_json(exclude_none=True, by_alias=True)
        await self._redis.set(self._get_job_key(job.id), job_json)
        await self._redis.publish(self._get_pubsub_channel(job.id), job_json)


_job_status_service: JobStatusService | None = None


async def get_job_status_service() -> JobStatusService:
    """
    Returns the singleton instance of the JobStatusService.
    """
    global _job_status_service
    if _job_status_service is None:
        redis_client = get_async_redis_client()
        _job_status_service = JobStatusService(redis_client)
    return _job_status_service
