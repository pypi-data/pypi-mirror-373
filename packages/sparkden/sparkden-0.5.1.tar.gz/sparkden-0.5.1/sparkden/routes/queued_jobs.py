import asyncio
from typing import Annotated, AsyncGenerator

from litestar import Controller, get
from litestar.di import Provide
from litestar.plugins.pydantic import PydanticDTO
from litestar.response import ServerSentEvent, ServerSentEventMessage
from sparkden.models.shared import BaseModel
from sparkden.queued_job.models import QueuedJob, QueuedJobStatus
from sparkden.queued_job.service import JobStatusService, get_job_status_service
from sparkden.shared.utils import dto_config


class GetQueuedJobResponse(BaseModel):
    job: QueuedJob | None = None
    error: str | None = None


GetQueuedJobResponseDTO = PydanticDTO[Annotated[GetQueuedJobResponse, dto_config()]]


async def provide_job_status_service() -> JobStatusService:
    return await get_job_status_service()


class QueuedJobController(Controller):
    path = "/jobs"
    dependencies = {
        "job_service": Provide(provide_job_status_service),
    }

    @get("/{job_id:str}", return_dto=GetQueuedJobResponseDTO)
    async def get_job(
        self, job_service: JobStatusService, job_id: str
    ) -> GetQueuedJobResponse:
        job = await job_service.get_job(job_id)
        return GetQueuedJobResponse(job=job)

    @get("/{job_id:str}/progress")
    async def job_events(
        self, job_service: JobStatusService, job_id: str
    ) -> ServerSentEvent:
        async def event_generator() -> AsyncGenerator[ServerSentEventMessage, None]:
            # Poll for the job to appear, with a timeout.
            initial_job = None
            for _ in range(10):  # Poll for 10 seconds
                initial_job = await job_service.get_job(job_id)
                if initial_job:
                    break
                await asyncio.sleep(1)

            if not initial_job:
                yield ServerSentEventMessage(
                    data=GetQueuedJobResponse(
                        error="Job not found",
                    ).model_dump_json(exclude_none=True, by_alias=True),
                    event="message",
                )
                return

            yield ServerSentEventMessage(
                data=GetQueuedJobResponse(
                    job=initial_job,
                ).model_dump_json(exclude_none=True, by_alias=True),
                event="message",
            )

            if initial_job.status in [QueuedJobStatus.SUCCESS, QueuedJobStatus.FAILURE]:
                return

            # Then, subscribe to updates
            pubsub = job_service._redis.pubsub()
            await pubsub.subscribe(job_service._get_pubsub_channel(job_id))

            while True:
                try:
                    message = await pubsub.get_message(
                        ignore_subscribe_messages=True, timeout=10
                    )
                    if message and message["type"] == "message":
                        data = message["data"]
                        job_data = QueuedJob.model_validate_json(data)
                        yield ServerSentEventMessage(
                            data=GetQueuedJobResponse(
                                job=job_data,
                            ).model_dump_json(exclude_none=True, by_alias=True),
                            event="message",
                        )
                        # If the job is finished, break the loop
                        if job_data.status in [
                            QueuedJobStatus.SUCCESS,
                            QueuedJobStatus.FAILURE,
                        ]:
                            break
                    await asyncio.sleep(1)
                except asyncio.CancelledError:
                    await pubsub.unsubscribe(job_service._get_pubsub_channel(job_id))
                    break

        return ServerSentEvent(content=event_generator())
