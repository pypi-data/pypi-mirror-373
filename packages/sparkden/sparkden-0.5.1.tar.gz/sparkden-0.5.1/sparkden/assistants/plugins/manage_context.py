from typing import Callable

from google.adk.agents.callback_context import CallbackContext
from google.adk.events.event import Event
from google.adk.flows.llm_flows.contents import _get_contents
from google.adk.models.llm_request import LlmRequest
from google.adk.models.llm_response import LlmResponse
from google.adk.plugins.base_plugin import BasePlugin
from google.genai import types


class ManageContextPlugin(BasePlugin):
    def __init__(
        self,
        clear_after_transfer: bool | list[str] = False,
        filter_events: Callable[[list[Event], CallbackContext], list[Event]]
        | None = None,
    ):
        super().__init__(name="manage_context")
        self.clear_after_transfer = clear_after_transfer
        self.filter_events = filter_events

    async def before_model_callback(
        self, *, callback_context: CallbackContext, llm_request: LlmRequest
    ) -> LlmResponse | None:
        events = callback_context._invocation_context.session.events
        if not events:
            return None

        if self.clear_after_transfer:
            if (
                not isinstance(self.clear_after_transfer, list)
                or callback_context.agent_name in self.clear_after_transfer
            ):
                start_index = 0
                for idx, event in reversed(list(enumerate(events))):
                    if (
                        event.author != callback_context.agent_name
                        and event.author != "user"
                    ):
                        start_index = min(idx + 1, len(events) - 1)
                        break
                events = events[start_index:]

        if self.filter_events:
            events = self.filter_events(events, callback_context)

        llm_request.contents = _get_contents(
            callback_context._invocation_context.branch,
            events,
            callback_context.agent_name,
        )

        if not llm_request.contents or llm_request.contents[0].role != "user":
            llm_request.contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part(
                            text="Handle the requests as specified in the System Instruction."
                        )
                    ],
                )
            ] + llm_request.contents
