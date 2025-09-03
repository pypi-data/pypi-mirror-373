import inspect
import logging
from typing import Any

from google.adk.tools import BaseTool, ToolContext
from google.genai import types
from pydantic import BaseModel
from typing_extensions import override

from sparkden.models.assistant import (
    ToolResponse,
    ToolResponseStatus,
    UserApprovalResult,
)

from ..helpers import validate_tool_param

logger = logging.getLogger(__name__)


class UserApprovalTool(BaseTool):
    item_name: str
    item_type: type[BaseModel]

    ITEM_PARAM_NAME = "item_to_approve"

    def __init__(self, item_name: str, item_type: type[BaseModel], description: str):
        self.item_name = item_name
        self.item_type = item_type
        super().__init__(
            name=f"request_{item_name}_approval",
            description=inspect.cleandoc(description),
            is_long_running=True,
        )

    @override
    def _get_declaration(self) -> types.FunctionDeclaration | None:
        # Get JSON schema for the item_type parameter
        item_schema = self.item_type.model_json_schema()

        # Create the parameters schema with the item_key as the property
        parameters_schema = types.JSONSchema.model_validate(
            {
                "type": "object",
                "properties": {self.ITEM_PARAM_NAME: item_schema},
                "required": [self.ITEM_PARAM_NAME],
                "additionalProperties": False,
            }
        )

        # Create the response schema for ToolResponse
        response_schema = types.JSONSchema.model_validate(
            {
                "type": "object",
                "properties": {
                    "result": UserApprovalResult.model_json_schema(),
                    "status": {
                        "type": "string",
                        "enum": ["pending", "success", "error"],
                        "description": "The status of the tool response",
                    },
                    "error": {
                        "type": "string",
                        "description": "The error message of the tool response",
                    },
                },
                "additionalProperties": False,
            }
        )

        return types.FunctionDeclaration(
            name=self.name,
            description=self.description,
            parameters=types.Schema.from_json_schema(json_schema=parameters_schema),
            response=types.Schema.from_json_schema(json_schema=response_schema),
        )

    @override
    async def run_async(
        self, *, args: dict[str, Any], tool_context: ToolContext
    ) -> ToolResponse:
        if self.ITEM_PARAM_NAME not in args:
            error_str = f"""Invoking `{self.name}()` failed as the following mandatory input parameters are not present:
{self.ITEM_PARAM_NAME}
You could retry calling this tool, but it is IMPORTANT for you to provide all the mandatory parameters."""
            return ToolResponse(
                status=ToolResponseStatus.ERROR,
                error=error_str,
            )

        validation_error = validate_tool_param(
            self.name, args[self.ITEM_PARAM_NAME], self.item_type
        )
        if validation_error:
            return validation_error

        tool_context.actions.skip_summarization = True
        return ToolResponse(
            result=None,
            status=ToolResponseStatus.PENDING,
        )
