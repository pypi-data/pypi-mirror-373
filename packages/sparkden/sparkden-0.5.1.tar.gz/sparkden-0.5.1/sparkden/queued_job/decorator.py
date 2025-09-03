import functools

import dramatiq
from dramatiq.middleware import CurrentMessage

from .models import JobFunction, JobResult, QueuedJob
from .service import JobStatusService


class JobContext:
    _service: JobStatusService
    job: QueuedJob

    def __init__(self, service: JobStatusService, job: QueuedJob):
        self._service = service
        self.job = job

    @property
    def job_id(self) -> str:
        return self.job.id

    @property
    def user_id(self) -> str:
        return self.job.user_id

    async def update_progress(
        self,
        progress: int,
        message: str | None = None,
        custom_status: str | None = None,
    ):
        self.job = await self._service.update_job_progress(
            self.job_id, progress, message, custom_status
        )


def queued_job(
    *,
    queue_name: str = "default",
    max_retries: int = 3,
    **dramatiq_options,
):
    def decorator(func: JobFunction) -> JobFunction:
        @dramatiq.actor(
            queue_name=queue_name,
            max_retries=max_retries,
            store_results=True,
            **dramatiq_options,
        )
        @functools.wraps(func)
        async def wrapper(user_id: str | None = None, **kwargs) -> JobResult:
            from sparkden.queued_job.service import get_job_status_service

            service = await get_job_status_service()

            message = CurrentMessage.get_current_message()
            if message is None:
                raise ValueError("Could not get current message")
            job_id = message.message_id
            if user_id is None:
                user_id = "anonymous"

            job = await service.create_job(job_id, user_id)
            context = JobContext(service, job)

            try:
                await service.mark_job_as_running(job_id)

                # Remove user_id from kwargs before passing to the original function
                kwargs.pop("user_id", None)
                # Call the original function with the context
                result = await func(context, **kwargs)

                await service.mark_job_as_success(job_id, result or {})
                return result

            except Exception as e:
                await service.mark_job_as_failure(job_id, str(e))
                raise

        return wrapper

    return decorator
