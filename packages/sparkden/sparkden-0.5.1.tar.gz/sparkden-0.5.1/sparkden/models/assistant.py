from abc import ABC
from enum import StrEnum
from typing import Callable, NotRequired, Sequence, TypedDict

from google.adk.agents import BaseAgent
from google.adk.plugins.base_plugin import BasePlugin
from litestar import Controller
from litestar.datastructures import UploadFile
from litestar.handlers import ASGIRouteHandler
from pydantic import Field, field_serializer
from sparkden.assistants.context_selector import ContextSelector
from sparkden.models.knowledge import DataSourceCreator
from sparkden.models.shared import BaseModel, ExtraInfoMixin


class ToolResponseStatus(StrEnum):
    PENDING = "pending"
    SUCCESS = "success"
    ERROR = "error"


class ToolResponse[ResultT](TypedDict):
    """The base tool response."""

    result: NotRequired[ResultT]
    """The result of the tool."""

    status: NotRequired[ToolResponseStatus]
    """The status of the tool response."""

    error: NotRequired[str]
    """The error message of the tool response."""


class UserApprovalResult[ItemT](BaseModel):
    """The user approval result."""

    approved: bool
    """Whether the user approved the request."""

    feedback: str
    """The feedback for the user approval."""

    modified_item: ItemT | None = None
    """A modified item provided on approval as result, or on rejection as a suggestion."""


class ProgressItemStatus(StrEnum):
    COMPLETED = "completed"
    RUNNING = "running"
    PENDING = "pending"


AssistantApiRoute = type[Controller] | ASGIRouteHandler


class ContextOption(ExtraInfoMixin, BaseModel):
    id: str
    name: str
    description: str | None = None


class ContextWithFile(ContextOption):
    creator_id: str
    file: UploadFile | None = None


class ContextCreator(DataSourceCreator, ABC):
    context_selector: ContextSelector | None = None

    @field_serializer("context_selector")
    def serialize_context_selector(
        self, context_selector: ContextSelector | None
    ) -> bool:
        return context_selector is not None


class Assistant(BaseModel):
    id: str
    disabled: bool = False
    root_agent: BaseAgent = Field(exclude=True)
    api_routes: Sequence[AssistantApiRoute] | None = Field(default=None, exclude=True)
    agent_plugins: list[BasePlugin] = Field(default_factory=list, exclude=True)
    callbacks: dict[str, Callable] | None = Field(default=None, exclude=True)
    context_creators: list[ContextCreator] | None = None
    search_knowledge: str | None = None
    sequence: int = 9999

    def get_context_creator(self, creator_id: str) -> ContextCreator | None:
        return next(
            (
                context_creator
                for context_creator in self.context_creators or []
                if context_creator.id == creator_id
            ),
            None,
        )
