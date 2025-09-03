import uuid
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

import dramatiq

from .progress import JobProgressNotifier


class QueuedJobHandler(ABC):
    """Base class for handling queued jobs."""

    _job_worker: Any

    def __init__(self, job_type: str):
        self.job_type = job_type
        self.progress_notifier = JobProgressNotifier()

    @abstractmethod
    async def handle_job(self, job_id: str, user_id: str, **kwargs) -> Dict[str, Any]:
        """
        Handle the specific queued job.

        Args:
            job_id: Job ID
            user_id: User ID
            **kwargs: Job parameters

        Returns:
            Job result dict
        """
        pass

    async def notify_job_progress(
        self,
        job_id: str,
        progress_percent: int,
        message: str,
        user_id: str,
        database_id: Optional[str] = None,
        **extra_data,
    ):
        """Send notification about job progress."""
        await self.progress_notifier.notify(
            job_id=job_id,
            progress_percent=progress_percent,
            message=message,
            user_id=user_id,
            database_id=database_id,
            **extra_data,
        )


def queued_job(
    *,
    queue_name: str = "default",
    max_retries: int = 3,
    min_backoff: int = 15000,
    max_backoff: int = 300000,
    **dramatiq_options,
):
    """
    Decorator to create a queued job.

    Args:
        queue_name: Job queue name
        max_retries: Maximum number of retries
        min_backoff: Minimum backoff time (milliseconds)
        max_backoff: Maximum backoff time (milliseconds)
        **dramatiq_options: Other options for Dramatiq actor
    """

    def decorator(handler_class: type[QueuedJobHandler]):
        handler = handler_class(job_type=handler_class.__name__)

        @dramatiq.actor(
            queue_name=queue_name,
            max_retries=max_retries,
            min_backoff=min_backoff,
            max_backoff=max_backoff,
            actor_name=f"{handler.job_type}_worker",
            store_results=True,  # Enable result storage
            **dramatiq_options,
        )
        async def job_worker(
            job_id: Optional[str] = None, user_id: Optional[str] = None, **kwargs
        ):
            """Dramatiq job worker"""
            if job_id is None:
                job_id = str(uuid.uuid4())

            if not user_id:
                user_id = "anonymous"

            try:
                await handler.notify_job_progress(
                    job_id, 0, f"Job {handler.job_type} started", user_id
                )

                result = await handler.handle_job(job_id, user_id, **kwargs)

                await handler.notify_job_progress(
                    job_id, 100, f"Job {handler.job_type} completed", user_id
                )

                return result

            except Exception as e:
                await handler.notify_job_progress(
                    job_id, -1, f"Job {handler.job_type} failed: {str(e)}", user_id
                )
                raise

        # Use the job type as the function name to avoid conflicts
        job_worker.__name__ = f"{handler.job_type}_worker"

        # Attach the job worker to the handler class
        handler_class._job_worker = job_worker
        return handler_class

    return decorator
