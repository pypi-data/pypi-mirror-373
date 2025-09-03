from datetime import datetime
from enum import StrEnum
from typing import Any, Awaitable, Callable

from sparkden.models.shared import BaseModel


class QueuedJobStatus(StrEnum):
    PENDING = "pending"
    RUNNING = "running"
    SUCCESS = "success"
    FAILURE = "failure"


JobResult = dict[str, Any] | None

JobFunction = Callable[..., Awaitable[JobResult]]


class QueuedJob(BaseModel):
    id: str
    user_id: str
    status: QueuedJobStatus = QueuedJobStatus.PENDING
    progress: int = 0
    custom_status: str | None = None
    result: JobResult = None
    error: str | None = None
    created_at: datetime
    updated_at: datetime
