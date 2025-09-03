from typing import TYPE_CHECKING, Callable, Sequence

if TYPE_CHECKING:
    from sparkden.models.assistant import Assistant, AssistantApiRoute


class AssistantRegistry:
    """Assistant registry for managing registered assistants."""

    def __init__(self, assistants: "list[Assistant]" = []):
        """Initialize the assistant registry."""
        self._assistants: dict[str, Assistant] = {
            assistant.id: assistant for assistant in assistants
        }

    def register(
        self,
        assistant: "Assistant",
    ) -> "Assistant":
        """
        Register a new assistant.

        Args:
            assistant: The assistant to register

        Returns:
            The registered Assistant instance

        Raises:
            ValueError: If an assistant with the same ID is already registered
        """
        from google.adk.agents import LlmAgent

        from sparkden.assistants.helpers import assistant_context_collection_id
        from sparkden.assistants.tools.search_context_tool import search_context
        from sparkden.assistants.tools.search_knowledge_tool import SearchKnowledgeTool
        from sparkden.knowledge.registry import knowledge_collections
        from sparkden.models.knowledge import KnowledgeCollection

        if assistant.id in self._assistants:
            raise ValueError(
                f"Assistant with ID '{assistant.id}' is already registered"
            )

        self._assistants[assistant.id] = assistant

        if assistant.context_creators:
            knowledge_collections.register(
                KnowledgeCollection(
                    id=assistant_context_collection_id(assistant.id),
                    data_source_creators=assistant.context_creators,
                )
            )

            if isinstance(assistant.root_agent, LlmAgent):
                assistant.root_agent.tools.append(search_context)

        if assistant.search_knowledge and isinstance(assistant.root_agent, LlmAgent):
            assistant.root_agent.tools.append(
                SearchKnowledgeTool(collection_id=assistant.search_knowledge)
            )

        return assistant

    def get_assistant(self, id: str) -> "Assistant | None":
        """
        Get an assistant by ID.

        Args:
            id: The assistant ID

        Returns:
            The assistant if found, None otherwise
        """
        return self._assistants.get(id)

    def get_assistants(self, include_disabled: bool = False) -> "list[Assistant]":
        """
        Get all registered assistants.

        Args:
            include_disabled: Whether to include disabled assistants (default: True)

        Returns:
            List of assistants sorted by sequence
        """
        assistants = []
        if include_disabled:
            assistants = list(self._assistants.values())
        else:
            assistants = [a for a in self._assistants.values() if not a.disabled]

        # Sort by sequence, then by ID for consistent ordering
        return sorted(assistants, key=lambda a: (a.sequence, a.id))

    def unregister(self, id: str) -> bool:
        """
        Unregister an assistant by ID.

        Args:
            id: The assistant ID

        Returns:
            True if the assistant was found and removed, False otherwise
        """
        if id in self._assistants:
            del self._assistants[id]
            return True
        return False

    def is_registered(self, id: str) -> bool:
        """
        Check if an assistant is registered.

        Args:
            id: The assistant ID

        Returns:
            True if the assistant is registered, False otherwise
        """
        return id in self._assistants

    def enable_assistant(self, id: str) -> bool:
        """
        Enable an assistant by ID.

        Args:
            id: The assistant ID

        Returns:
            True if the assistant was found and enabled, False otherwise
        """
        assistant = self._assistants.get(id)
        if assistant:
            assistant.disabled = False
            return True
        return False

    def disable_assistant(self, id: str) -> bool:
        """
        Disable an assistant by ID.

        Args:
            id: The assistant ID

        Returns:
            True if the assistant was found and disabled, False otherwise
        """
        assistant = self._assistants.get(id)
        if assistant:
            assistant.disabled = True
            return True
        return False

    def update_sequence(self, id: str, sequence: int) -> bool:
        """
        Update the sequence of an assistant.

        Args:
            id: The assistant ID
            sequence: The new sequence value

        Returns:
            True if the assistant was found and updated, False otherwise
        """
        assistant = self._assistants.get(id)
        if assistant:
            assistant.sequence = sequence
            return True
        return False

    def clear(self) -> None:
        """Clear all registered assistants."""
        self._assistants.clear()

    def get_api_routes(self) -> "Sequence[AssistantApiRoute]":
        routes: "Sequence[AssistantApiRoute]" = []
        for assistant in self.get_assistants():
            if assistant.api_routes:
                routes.extend(assistant.api_routes)
        return routes

    def get_callbacks(self, callback_name: str) -> list[Callable]:
        callbacks = []
        for assistant in self.get_assistants():
            callback = (assistant.callbacks or {}).get(callback_name)
            if callback is not None:
                callbacks.append(callback)
        return callbacks


assistant_registry = AssistantRegistry()
