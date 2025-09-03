import uuid
from datetime import datetime
from typing import Any, Literal

from google.adk.events import Event
from google.adk.sessions import Session
from google.genai.types import FunctionCall, FunctionResponse
from sparkden.db.schema import Task as StorageTask
from sparkden.models.shared import BaseModel, ExtraInfoMixin
from sparkden.shared.utils import camelize_dict


class ContentPart(BaseModel):
    id: str
    thought: bool | None = None
    function_call: FunctionCall | None = None
    function_response: FunctionResponse | None = None
    text: str | None = None


class TaskMessage(BaseModel):
    id: str
    type: Literal["user", "assistant"]
    content: list[ContentPart]
    created_at: datetime
    partial: bool | None = None

    @classmethod
    def from_event(cls, event: Event) -> "TaskMessage":
        content_parts = (
            event.content.parts if event.content and event.content.parts else []
        )
        return TaskMessage(
            id=event.id,
            type="user" if event.author == "user" else "assistant",
            created_at=datetime.fromtimestamp(event.timestamp),
            content=[
                ContentPart(
                    id=str(uuid.uuid4()),
                    thought=part.thought,
                    function_call=part.function_call,
                    function_response=part.function_response,
                    text=part.text,
                )
                for part in content_parts
            ],
            partial=event.partial,
        )


class TaskItem(BaseModel):
    id: str
    assistant_id: str
    title: str
    updated_at: datetime

    @classmethod
    def from_storage(cls, task: "StorageTask") -> "TaskItem":
        return cls(
            id=str(task.id),
            assistant_id=task.assistant_id,
            title=task.title,
            updated_at=task.updated_at,
        )


class Task(ExtraInfoMixin, BaseModel):
    id: str
    assistant_id: str
    title: str
    messages: list[TaskMessage]
    state: dict[str, Any]
    updated_at: datetime

    @classmethod
    def from_storage(cls, task: StorageTask, session: Session) -> "Task":
        return cls(
            id=str(task.id),
            assistant_id=task.assistant_id,
            title=task.title,
            messages=[
                TaskMessage.from_event(event)
                for event in session.events
                if event.content
            ],
            state=camelize_dict(session.state),
            extra_info=task.extra_info,
            updated_at=task.updated_at,
        )


class TaskSSEData(BaseModel):
    message: TaskMessage | None = None
    state_delta: dict[str, Any] | None = None
    artifact_delta: dict[str, int] | None = None
    error_code: str | None = None
    error_message: str | None = None

    @classmethod
    def from_event(cls, event: Event) -> "TaskSSEData":
        message = (
            TaskMessage.from_event(event)
            if event.content and event.content.parts
            else None
        )
        state_delta = (
            camelize_dict(event.actions.state_delta) if event.actions else None
        )
        artifact_delta = (
            camelize_dict(event.actions.artifact_delta) if event.actions else None
        )

        return cls(
            message=message,
            state_delta=state_delta,
            artifact_delta=artifact_delta,
            error_code=event.error_code,
            error_message=event.error_message,
        )


class DataSourceContext(BaseModel):
    data_source_id: str
    creator_id: str
    name: str


class InlineContext(BaseModel):
    creator_id: str
    name: str
    content: str


class UserContentWithContext(BaseModel):
    contexts: list[DataSourceContext | InlineContext]
    instruction: str | None = None
