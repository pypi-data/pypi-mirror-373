from typing import Annotated, Any

from google.genai.types import Part
from litestar import Controller, Request, get, post
from litestar.datastructures import UploadFile
from litestar.di import Provide
from litestar.plugins.pydantic import PydanticDTO
from litestar.response import ServerSentEvent
from sparkden.models.assistant import ContextWithFile
from sparkden.models.shared import BaseModel, OffsetPagination
from sparkden.models.task import Task, TaskItem
from sparkden.services.task import TaskService
from sparkden.shared.utils import dto_config, snake_case_dict


class GetTaskResponse(BaseModel):
    task: Task | None


class CreateTaskParams(BaseModel):
    title: str
    assistant_id: str
    task_id: str | None = None


class SendMessageParams(BaseModel):
    assistant_id: str
    message: list[Part]
    state_delta: dict[str, Any] | None = None
    edit_message_id: str | None = None
    contexts: list[ContextWithFile] | None = None


CreateTaskParamsDTO = PydanticDTO[Annotated[CreateTaskParams, dto_config()]]
SendMessageParamsDTO = PydanticDTO[Annotated[SendMessageParams, dto_config()]]
TaskDTO = PydanticDTO[Annotated[Task, dto_config()]]
GetTaskResponseDTO = PydanticDTO[Annotated[GetTaskResponse, dto_config()]]
ListTasksResponseDTO = PydanticDTO[Annotated[OffsetPagination[TaskItem], dto_config()]]


def get_task_service(request: Request) -> TaskService:
    return TaskService(user_id=str(request.user.id))


class TaskController(Controller):
    path = "/tasks"
    dependencies = {
        "task_service": Provide(get_task_service, sync_to_thread=True),
    }
    request_max_body_size = 50 * 1024 * 1024  # 50MB

    @get("/", return_dto=ListTasksResponseDTO)
    async def list_tasks(
        self, task_service: TaskService, limit: int = 30, offset: int = 0
    ) -> OffsetPagination[TaskItem]:
        return await task_service.list_tasks(limit=limit, offset=offset)

    @post("/", dto=CreateTaskParamsDTO, return_dto=TaskDTO)
    async def create_task(
        self, task_service: TaskService, data: CreateTaskParams
    ) -> Task:
        return await task_service.create_task(
            title=data.title, assistant_id=data.assistant_id, task_id=data.task_id
        )

    @get("/{task_id:str}", return_dto=GetTaskResponseDTO)
    async def get_task(
        self, task_service: TaskService, task_id: str, assistant_id: str
    ) -> GetTaskResponse:
        task = await task_service.get_task(assistant_id=assistant_id, task_id=task_id)
        return GetTaskResponse(task=task)

    @post(
        "/{task_id:str}/run",
    )
    async def run_task(
        self,
        task_service: TaskService,
        task_id: str,
        request: Request,
    ) -> ServerSentEvent:
        form_data = await request.form()
        data = SendMessageParams.model_validate_json(form_data["payload"])

        if data.contexts:
            for context in data.contexts:
                file = form_data.get(context.id)
                if file and isinstance(file, UploadFile):
                    context.file = file

        return ServerSentEvent(
            task_service.run_task(
                assistant_id=data.assistant_id,
                task_id=task_id,
                message_content=data.message,
                state_delta=snake_case_dict(data.state_delta)
                if data.state_delta
                else None,
                edit_message_id=data.edit_message_id,
                contexts=data.contexts,
            )
        )
