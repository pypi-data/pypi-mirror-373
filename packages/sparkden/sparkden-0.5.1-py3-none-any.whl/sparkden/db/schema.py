from enum import StrEnum
from uuid import uuid4

from google.adk.sessions.database_session_service import StorageSession
from litestar.plugins.sqlalchemy import base
from sqlalchemy import ForeignKey, ForeignKeyConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column


class UserRole(StrEnum):
    ADMIN = "admin"
    USER = "user"


class DataSourceStatus(StrEnum):
    NOT_LOADED = "not_loaded"
    PROCESSING = "processing"
    READY = "ready"
    ERROR = "error"


class User(base.UUIDAuditBase):
    __tablename__ = "users"
    id: Mapped[str] = mapped_column(default=lambda: str(uuid4()), primary_key=True)
    name: Mapped[str]
    username: Mapped[str | None]
    password: Mapped[bytes | None]
    avatar: Mapped[str | None]
    role: Mapped[UserRole] = mapped_column(default=UserRole.USER)
    extra_info: Mapped[dict | None] = mapped_column(JSONB)


class ApiKey(base.UUIDAuditBase):
    __tablename__ = "api_keys"
    key_hash: Mapped[str] = mapped_column(unique=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    revoked: Mapped[bool] = mapped_column(default=False)


class KnowledgeDataSource(base.UUIDAuditBase):
    __tablename__ = "knowledge_data_sources"
    __table_args__ = (
        Index("idx_knowledge_data_sources_collection_id", "collection_id"),
    )

    name: Mapped[str]
    creator_id: Mapped[str]
    status: Mapped[DataSourceStatus]
    extra_info: Mapped[dict | None] = mapped_column(JSONB)
    collection_id: Mapped[str]


class Task(base.UUIDAuditBase):
    __tablename__ = "tasks"
    __table_args__ = (
        Index("idx_tasks_agent_session_id", "agent_session_id"),
        Index("idx_tasks_user_id_assistant_id", "user_id", "assistant_id"),
        ForeignKeyConstraint(
            ["assistant_id", "user_id", "agent_session_id"],
            [StorageSession.app_name, StorageSession.user_id, StorageSession.id],
            ondelete="CASCADE",
        ),
    )

    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    assistant_id: Mapped[str]
    agent_session_id: Mapped[str]
    title: Mapped[str]
    extra_info: Mapped[dict | None] = mapped_column(JSONB)
