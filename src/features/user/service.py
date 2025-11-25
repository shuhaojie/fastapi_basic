from sqlalchemy import select
from src.features.auth.models import User


class UserService:

    @staticmethod
    def get_user_list(q):
        query = select(User).where(User.is_deleted == 0)
        if q:
            query = query.where(User.username.ilike(f"%{q}"))
        return query


user_service = UserService()
