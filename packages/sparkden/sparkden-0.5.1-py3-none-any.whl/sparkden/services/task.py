import json
from datetime import datetime
from typing import Any, AsyncGenerator
from zoneinfo import ZoneInfo

from google.adk.agents.run_config import RunConfig, StreamingMode
from google.adk.runners import Runner
from google.adk.sessions.database_session_service import StorageEvent
from google.genai import types
from litestar.response import ServerSentEventMessage
from sparkden.adk.session_service import SessionService
from sparkden.assistants import assistants
from sparkden.assistants.helpers import assistant_context_collection_id
from sparkden.knowledge.data_loader import DataLoader
from sparkden.models.assistant import Assistant, ContextWithFile
from sparkden.models.knowledge import FileObject, KnowledgeDataSourceCreate
from sparkden.models.shared import OffsetPagination
from sparkden.services.base import BaseService
from sparkden.services.knowledge import KnowledgeService
from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession

from ..db.schema import Task as StorageTask
from ..models.task import (
    DataSourceContext,
    InlineContext,
    Task,
    TaskItem,
    TaskSSEData,
    UserContentWithContext,
)


class TaskService(BaseService):
    def __init__(self, user_id: str):
        super().__init__(user_id=user_id)
        self.agent_session_service = SessionService()
        self.knowledge_service = KnowledgeService(user_id=user_id)

    async def list_tasks(
        self, *, limit: int = 30, offset: int = 0
    ) -> OffsetPagination[TaskItem]:
        async with self.db_session_maker.begin() as db_session:
            query = (
                select(
                    StorageTask,
                    func.count().over().label("total_count"),
                )
                .where(StorageTask.user_id == self.user_id)
                .order_by(StorageTask.updated_at.desc())
                .offset(offset)
                .limit(limit)
            )
            result = (await db_session.execute(query)).all()
            tasks = [TaskItem.from_storage(row[0]) for row in result]
            total = result[0][1] if result else 0

        return OffsetPagination(
            items=tasks,
            total=total,
            limit=limit,
            offset=offset,
        )

    async def create_task(
        self, *, title: str, assistant_id: str, task_id: str | None = None
    ) -> Task:
        async with self.db_session_maker.begin() as db_session:
            session = await self.agent_session_service.create_session(
                app_name=assistant_id,
                user_id=self.user_id,
                state={
                    "start_time": datetime.now(
                        tz=ZoneInfo("Asia/Shanghai")
                    ).isoformat(),
                },
                db_session=db_session,
            )

            task_attributes = {
                "user_id": self.user_id,
                "assistant_id": assistant_id,
                "title": title,
                "agent_session_id": session.id,
            }
            if task_id:
                task_attributes["id"] = task_id

            task = await db_session.scalar(
                insert(StorageTask)
                .values(
                    **task_attributes,
                )
                .returning(StorageTask)
            )
            if not task:
                raise Exception("Failed to create task")

        return Task.from_storage(task, session)

    async def get_task(self, *, assistant_id: str, task_id: str) -> Task | None:
        async with self.db_session_maker.begin() as db_session:
            task = await db_session.scalar(
                select(StorageTask).where(
                    StorageTask.user_id == self.user_id,
                    StorageTask.assistant_id == assistant_id,
                    StorageTask.id == task_id,
                )
            )

            if task is None:
                return None

            session = await self.agent_session_service.get_session(
                user_id=self.user_id,
                app_name=assistant_id,
                session_id=task.agent_session_id,
                db_session=db_session,
            )

        return Task.from_storage(task, session) if session else None

    async def run_task(
        self,
        *,
        assistant_id: str,
        task_id: str,
        message_content: list[types.Part],
        state_delta: dict[str, Any] | None = None,
        edit_message_id: str | None = None,
        contexts: list[ContextWithFile] | None = None,
    ) -> AsyncGenerator[ServerSentEventMessage, None]:
        assistant = assistants.get_assistant(assistant_id)
        if assistant is None:
            raise ValueError(f"Assistant {assistant_id} not found")

        async with self.db_session_maker.begin() as db_session:
            task = await db_session.get(StorageTask, task_id)
            if task is None:
                raise ValueError(f"Task {task_id} not found")
            session_id = task.agent_session_id

            # truncate events from the message_id
            if edit_message_id:
                await self._truncate_events_after_id(
                    session_id=session_id,
                    event_id=edit_message_id,
                    db_session=db_session,
                )

        context_content: list[types.Part] = []
        if contexts:
            task_contexts: list[DataSourceContext | InlineContext] = []
            for context in contexts:
                task_context = await self._generate_task_context(assistant, context)
                task_contexts.append(task_context)

            if task_contexts:
                user_content_with_context = UserContentWithContext(
                    contexts=task_contexts,
                    instruction="If context already has content, use content directly, otherwise call the search_context tool with data_source_id to retrieve information.",
                )
                context_content.append(
                    types.Part(
                        text=user_content_with_context.model_dump_json(
                            exclude_none=True,
                            by_alias=True,
                        )
                    )
                )

        new_message = types.Content(
            role="user",
            parts=message_content + context_content,
        )

        runner = Runner(
            app_name=assistant_id,
            agent=assistant.root_agent,
            session_service=self.agent_session_service,
            plugins=[
                *assistant.agent_plugins,
            ],
        )

        accumulated_text = ""
        user_event_yielded = False

        async for event in runner.run_async(
            user_id=self.user_id,
            session_id=session_id,
            new_message=new_message,
            run_config=RunConfig(streaming_mode=StreamingMode.SSE),
            state_delta=state_delta,
        ):
            if not user_event_yielded:
                async with self.db_session_maker.begin() as db_session:
                    # get recent user event
                    user_event = await db_session.scalar(
                        select(StorageEvent)
                        .where(
                            StorageEvent.session_id == session_id,
                            StorageEvent.author == "user",
                        )
                        .order_by(StorageEvent.timestamp.desc())
                        .limit(1)
                    )
                if user_event is not None:
                    user_event_yielded = True
                    yield ServerSentEventMessage(
                        event="message",
                        data=TaskSSEData.from_event(
                            user_event.to_event(),
                        ).model_dump_json(
                            exclude_none=True,
                            by_alias=True,
                        ),
                    )

            event_name, event_data = None, None
            if event.partial:
                event_name = "message/partial"
                accumulated_event = event.model_copy(deep=True)
                if (
                    accumulated_event.content
                    and accumulated_event.content.parts
                    and accumulated_event.content.parts[0].text
                ):
                    accumulated_text += accumulated_event.content.parts[0].text
                    accumulated_event.content.parts[0].text = accumulated_text
                # TODO: support partial function call
                event_data = TaskSSEData.from_event(
                    accumulated_event,
                ).model_dump_json(exclude_none=True, by_alias=True)
            else:
                accumulated_text = ""
                event_name = "message"
                event_data = TaskSSEData.from_event(
                    event,
                ).model_dump_json(
                    exclude_none=True,
                    by_alias=True,
                )
            yield ServerSentEventMessage(
                data=event_data,
                event=event_name,
            )

    async def _truncate_events_after_id(
        self, *, session_id: str, event_id: str, db_session: AsyncSession
    ) -> None:
        """
        Truncate the events after the event_id (ADK session operation only)
        """
        event = await db_session.scalar(
            select(StorageEvent).where(
                StorageEvent.id == event_id, StorageEvent.session_id == session_id
            )
        )
        if event is None:
            return

        deleted_event_ids = await db_session.scalars(
            delete(StorageEvent)
            .where(
                StorageEvent.session_id == session_id,
                StorageEvent.timestamp >= event.timestamp,
            )
            .returning(StorageEvent.id)
        )

        # call on_events_deleted callbacks
        callbacks = assistants.get_callbacks("on_events_deleted")
        for callback in callbacks:
            callback(deleted_event_ids.all(), db_session)

    async def _generate_task_context(
        self, assistant: Assistant, context: ContextWithFile
    ) -> DataSourceContext | InlineContext:
        context_creator = assistant.get_context_creator(context.creator_id)
        if not context_creator:
            raise ValueError(f"Context creator {context.creator_id} not found")

        extra_info = {
            **(context_creator.extra_info or {}),
            **(context.extra_info or {}),
        }
        if context.file:
            extra_info["file"] = FileObject(
                name=context.file.filename,
                content=await context.file.read(),
                content_type=context.file.content_type,
            )

        data_source, _, _ = await self.knowledge_service.add_data_source(
            KnowledgeDataSourceCreate(
                collection_id=assistant_context_collection_id(assistant.id),
                creator_id=context.creator_id,
                name=context.name,
                extra_info=extra_info,
            ),
            auto_load=False,
        )

        data_loader = DataLoader(data_source)
        parsed_result = await data_loader.parse()

        result_str = (
            parsed_result.data
            if isinstance(parsed_result.data, str)
            else json.dumps(parsed_result.data)
        )

        print(f"result_len: {len(result_str)}")
        if len(result_str) > 10000:
            return DataSourceContext(
                name=context.name,
                data_source_id=data_source.id,
                creator_id=context.creator_id,
            )
        else:
            return InlineContext(
                creator_id=context.creator_id,
                name=context.name,
                content=result_str,
            )
