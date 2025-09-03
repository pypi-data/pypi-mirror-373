import hashlib

from bcrypt import gensalt, hashpw
from google.adk.sessions.database_session_service import Base as ADKBase
from sparkden.shared.pg import get_engine, get_session_maker
from sparkden.shared.utils import getenv
from sqlalchemy import exists, insert, select
from sqlalchemy.exc import OperationalError

from .schema import ApiKey, User, UserRole, base


async def init_db() -> None:
    await seed_db()


async def seed_db() -> None:
    async with get_engine().begin() as conn:
        try:
            await conn.run_sync(ADKBase.metadata.create_all)
            await conn.run_sync(base.UUIDAuditBase.metadata.create_all)
        except OperationalError as exc:
            print(f"Could not create target metadata.  Reason: {exc}")

    async with get_session_maker().begin() as db_session:
        user_exists = await db_session.scalar(
            select(exists().where(User.id.is_not(None)))
        )
        if not user_exists:
            try:
                api_keys = getenv("API_KEYS", "").split(",")
                users_data = [
                    {
                        "name": user,
                        "username": f"test{index + 1}",
                        "password": hashpw("password123".encode(), gensalt()),
                        "extra_info": {"college": "计算机学院"},
                        "role": UserRole.ADMIN if index in [0, 1] else UserRole.USER,
                    }
                    for index, user in enumerate(users)
                ]
                user_ids = await db_session.scalars(
                    insert(User).values(users_data).returning(User.id)
                )

                if len(api_keys) > 0:
                    api_keys_data = [
                        {
                            "key_hash": hashlib.sha256(api_key.encode()).hexdigest(),
                            "user_id": user_id,
                        }
                        for user_id, api_key in zip(user_ids, api_keys)
                    ]
                    await db_session.execute(insert(ApiKey).values(api_keys_data))

                print(f"Successfully seeded {len(users)} users")
            except Exception as exc:
                print(f"Error seeding users: {exc}")
                raise


users = [
    "张三",
    "李四",
    "王五",
    "赵六",
    "孙七",
    "周八",
    "吴九",
    "郑十",
    "John Smith",
    "Alice Brown",
]
