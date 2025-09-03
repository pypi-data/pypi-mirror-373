import logging
from datetime import datetime
from typing import Any, cast, override

from google.adk.events import Event
from google.adk.sessions import Session
from google.adk.sessions.base_session_service import (
    BaseSessionService,
    GetSessionConfig,
    ListSessionsResponse,
)
from google.adk.sessions.database_session_service import (
    StorageAppState,
    StorageEvent,
    StorageSession,
    StorageUserState,
    _extract_state_delta,
    _merge_state,
)
from sparkden.shared.pg import get_session_maker
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession
from tzlocal import get_localzone

logger = logging.getLogger(__name__)


class SessionService(BaseSessionService):
    """A session service that uses a database for storage."""

    def __init__(self):
        # Get the local timezone
        local_timezone = get_localzone()
        logger.info(f"Local timezone: {local_timezone}")

    @override
    async def create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: dict[str, Any] | None = None,
        session_id: str | None = None,
        db_session: AsyncSession | None = None,
    ) -> Session:
        if db_session:
            return await self._create_session(
                app_name=app_name,
                user_id=user_id,
                state=state,
                session_id=session_id,
                db_session=db_session,
            )
        else:
            async with get_session_maker().begin() as db_session:
                return await self._create_session(
                    app_name=app_name,
                    user_id=user_id,
                    state=state,
                    session_id=session_id,
                    db_session=db_session,
                )

    async def _create_session(
        self,
        *,
        app_name: str,
        user_id: str,
        state: dict[str, Any] | None = None,
        session_id: str | None = None,
        db_session: AsyncSession,
    ) -> Session:
        # 1. Populate states.
        # 2. Build storage session object
        # 3. Add the object to the table
        # 4. Build the session object with generated id
        # 5. Return the session

        # Fetch app and user states from storage
        storage_app_state = await db_session.get(StorageAppState, (app_name))
        storage_user_state = await db_session.get(StorageUserState, (app_name, user_id))

        app_state = storage_app_state.state if storage_app_state else {}
        user_state = storage_user_state.state if storage_user_state else {}

        # Create state tables if not exist
        if not storage_app_state:
            storage_app_state = StorageAppState(app_name=app_name, state={})
            db_session.add(storage_app_state)
        if not storage_user_state:
            storage_user_state = StorageUserState(
                app_name=app_name, user_id=user_id, state={}
            )
            db_session.add(storage_user_state)

        # Extract state deltas
        app_state_delta, user_state_delta, session_state = _extract_state_delta(
            state  # type: ignore
        )

        # Apply state delta
        app_state.update(app_state_delta)
        user_state.update(user_state_delta)

        # Store app and user state
        if app_state_delta:
            storage_app_state.state = app_state  # type: ignore
        if user_state_delta:
            storage_user_state.state = user_state  # type: ignore

        # Store the session
        storage_session = StorageSession(
            app_name=app_name,
            user_id=user_id,
            id=session_id,
            state=session_state,
        )
        db_session.add(storage_session)
        await db_session.flush()
        await db_session.refresh(storage_session)

        # Merge states for response
        merged_state = _merge_state(app_state, user_state, session_state)
        session = storage_session.to_session(state=merged_state)
        return session

    @override
    async def get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: GetSessionConfig | None = None,
        db_session: AsyncSession | None = None,
    ) -> Session | None:
        if db_session:
            return await self._get_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                config=config,
                db_session=db_session,
            )
        else:
            async with get_session_maker().begin() as db_session:
                return await self._get_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id,
                    config=config,
                    db_session=db_session,
                )

    async def _get_session(
        self,
        *,
        app_name: str,
        user_id: str,
        session_id: str,
        config: GetSessionConfig | None = None,
        db_session: AsyncSession,
    ) -> Session | None:
        # 1. Get the storage session entry from session table
        # 2. Get all the events based on session id and filtering config
        # 3. Convert and return the session
        storage_session = await db_session.get(
            StorageSession, (app_name, user_id, session_id)
        )
        if storage_session is None:
            return None

        conditions = [
            StorageEvent.app_name == app_name,
            StorageEvent.session_id == storage_session.id,
            StorageEvent.user_id == user_id,
        ]

        if config and config.after_timestamp:
            after_dt = datetime.fromtimestamp(config.after_timestamp)
            conditions.append(StorageEvent.timestamp >= after_dt)

        stmt = (
            select(StorageEvent)
            .where(*conditions)
            .order_by(StorageEvent.timestamp.desc())
        )

        if config and config.num_recent_events:
            stmt = stmt.limit(config.num_recent_events)  # type: ignore

        storage_events = (await db_session.scalars(stmt)).all()

        # Fetch states from storage
        storage_app_state = await db_session.get(StorageAppState, app_name)
        storage_user_state = await db_session.get(StorageUserState, (app_name, user_id))

        app_state = storage_app_state.state if storage_app_state else {}
        user_state = storage_user_state.state if storage_user_state else {}
        session_state = storage_session.state

        # Merge states
        merged_state = _merge_state(app_state, user_state, session_state)

        # Convert storage session to session
        events = [e.to_event() for e in reversed(storage_events)]
        session = storage_session.to_session(state=merged_state, events=events)
        return session

    @override
    async def list_sessions(
        self,
        *,
        app_name: str,
        user_id: str,
        db_session: AsyncSession | None = None,
    ) -> ListSessionsResponse:
        if db_session:
            return await self._list_sessions(
                app_name=app_name,
                user_id=user_id,
                db_session=db_session,
            )
        else:
            async with get_session_maker().begin() as db_session:
                return await self._list_sessions(
                    app_name=app_name,
                    user_id=user_id,
                    db_session=db_session,
                )

    async def _list_sessions(
        self,
        *,
        app_name: str,
        user_id: str,
        db_session: AsyncSession,
    ) -> ListSessionsResponse:
        stmt = select(StorageSession).where(
            StorageSession.app_name == app_name,
            StorageSession.user_id == user_id,
        )
        results = (await db_session.scalars(stmt)).all()

        # Fetch states from storage
        storage_app_state = await db_session.get(StorageAppState, app_name)
        storage_user_state = await db_session.get(StorageUserState, (app_name, user_id))

        app_state = storage_app_state.state if storage_app_state else {}
        user_state = storage_user_state.state if storage_user_state else {}

        sessions = []
        for storage_session in results:
            session_state = storage_session.state
            merged_state = _merge_state(app_state, user_state, session_state)
            sessions.append(storage_session.to_session(state=merged_state))

        return ListSessionsResponse(sessions=sessions)

    @override
    async def delete_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        db_session: AsyncSession | None = None,
    ) -> None:
        if db_session:
            return await self._delete_session(
                app_name=app_name,
                user_id=user_id,
                session_id=session_id,
                db_session=db_session,
            )
        else:
            async with get_session_maker().begin() as db_session:
                return await self._delete_session(
                    app_name=app_name,
                    user_id=user_id,
                    session_id=session_id,
                    db_session=db_session,
                )

    async def _delete_session(
        self,
        app_name: str,
        user_id: str,
        session_id: str,
        db_session: AsyncSession,
    ) -> None:
        stmt = delete(StorageSession).where(
            StorageSession.app_name == app_name,
            StorageSession.user_id == user_id,
            StorageSession.id == session_id,
        )
        await db_session.execute(stmt)

    @override
    async def append_event(
        self, session: Session, event: Event, db_session: AsyncSession | None = None
    ) -> Event:
        if db_session:
            return await self._append_event(
                session=session,
                event=event,
                db_session=db_session,
            )
        else:
            async with get_session_maker().begin() as db_session:
                return await self._append_event(
                    session=session,
                    event=event,
                    db_session=db_session,
                )

    async def _append_event(
        self, session: Session, event: Event, db_session: AsyncSession
    ) -> Event:
        logger.info(f"Append event: {event} to session {session.id}")

        if event.partial:
            return event

        # 1. Check if timestamp is stale
        # 2. Update session attributes based on event config
        # 3. Store event to table
        storage_session = await db_session.get(
            StorageSession, (session.app_name, session.user_id, session.id)
        )

        if storage_session is None:
            raise ValueError(f"Session {session.id} not found")

        session_update_time = cast(datetime, storage_session.update_time).timestamp()

        if session_update_time > session.last_update_time:
            raise ValueError(
                "The last_update_time provided in the session object"
                f" {datetime.fromtimestamp(session.last_update_time):'%Y-%m-%d %H:%M:%S'} is"
                " earlier than the update_time in the storage_session"
                f" {datetime.fromtimestamp(session_update_time):'%Y-%m-%d %H:%M:%S'}."
                " Please check if it is a stale session."
            )

        # Fetch states from storage
        storage_app_state = await db_session.get(StorageAppState, session.app_name)
        storage_user_state = await db_session.get(
            StorageUserState, (session.app_name, session.user_id)
        )

        app_state = storage_app_state.state if storage_app_state else {}
        user_state = storage_user_state.state if storage_user_state else {}
        session_state = storage_session.state

        # Extract state delta
        app_state_delta = {}
        user_state_delta = {}
        session_state_delta = {}
        if event.actions and event.actions.state_delta:
            app_state_delta, user_state_delta, session_state_delta = (
                _extract_state_delta(event.actions.state_delta)
            )

        # Merge state and update storage
        if app_state_delta:
            app_state.update(app_state_delta)
            storage_app_state.state = app_state  # type: ignore
        if user_state_delta:
            user_state.update(user_state_delta)
            storage_user_state.state = user_state  # type: ignore
        if session_state_delta:
            session_state.update(session_state_delta)
            storage_session.state = session_state

        db_session.add(StorageEvent.from_event(session, event))
        await db_session.flush()
        await db_session.refresh(storage_session)

        # Update timestamp with commit time
        session.last_update_time = cast(
            datetime, storage_session.update_time
        ).timestamp()

        # Also update the in-memory session
        await super().append_event(session=session, event=event)
        return event
