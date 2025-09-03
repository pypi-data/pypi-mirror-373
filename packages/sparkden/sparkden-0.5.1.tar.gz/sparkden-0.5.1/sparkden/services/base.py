from ..shared.pg import get_engine, get_session_maker


class BaseService:
    def __init__(self, *, user_id: str):
        self.user_id = user_id
        self.db_engine = get_engine()
        self.db_session_maker = get_session_maker()
