from typing import Annotated

from litestar import Controller, Request, get
from litestar.exceptions import NotFoundException
from litestar.plugins.pydantic import PydanticDTO
from sparkden.models.assistant import ContextOption
from sparkden.models.shared import BaseModel
from sparkden.shared.utils import dto_config


class ListContextOptionsResponse(BaseModel):
    context_options: list[ContextOption]


ListContextOptionsResponseDTO = PydanticDTO[
    Annotated[ListContextOptionsResponse, dto_config()]
]


class AssistantController(Controller):
    path = "/assistants"

    @get("/", sync_to_thread=True)
    def list_assistants(self) -> list[dict]:
        from sparkden.assistants import assistants

        return [
            assistant.model_dump(by_alias=True)
            for assistant in assistants.get_assistants(include_disabled=True)
        ]

    @get(
        "/{assistant_id:str}/context-creators/{context_creator_id:str}",
        return_dto=ListContextOptionsResponseDTO,
    )
    async def get_context_options(
        self,
        assistant_id: str,
        context_creator_id: str,
        request: Request,
        search_query: str | None = None,
    ) -> ListContextOptionsResponse:
        from sparkden.assistants import assistants

        assistant = assistants.get_assistant(assistant_id)
        if assistant is None:
            raise NotFoundException(f"Assistant {assistant_id} not found")

        context_creator = assistant.get_context_creator(context_creator_id)
        if context_creator is None:
            raise NotFoundException(f"Context creator {context_creator_id} not found")

        if context_creator.context_selector is None:
            raise NotFoundException(
                f"Context selector for {context_creator_id} not found"
            )

        context_options = await context_creator.context_selector.context_options(
            user_id=str(request.user.id), search_query=search_query
        )

        return ListContextOptionsResponse(context_options=context_options)
