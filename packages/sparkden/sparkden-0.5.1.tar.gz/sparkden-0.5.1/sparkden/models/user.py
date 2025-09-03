from sparkden.db.schema import User as StorageUser
from sparkden.db.schema import UserRole
from sparkden.models.shared import BaseModel
from sparkden.shared.utils import getenv

ADMIN_USERS = [username.strip() for username in getenv("ADMIN_USERS", "").split(",")]


class User(BaseModel):
    id: str
    name: str
    username: str | None
    avatar: str | None
    role: UserRole
    extra_info: dict | None

    @classmethod
    def from_storage(cls, user: StorageUser) -> "User":
        return cls(
            id=user.id,
            name=user.name,
            username=user.username,
            avatar=user.avatar,
            role=user.role,
            extra_info=user.extra_info,
        )

    @property
    def is_admin(self) -> bool:
        return self.role == UserRole.ADMIN or self.username in ADMIN_USERS
