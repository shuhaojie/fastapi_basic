from typing import Tuple
from sqlalchemy import select, update
from src.features.user.models import User
from src.core.server.dependencies import DbSession
from src.features.user.schema import UpdateUserSchema


class UserService:

    @staticmethod
    def get_user_list(q: str):
        query = select(User).where(User.is_deleted == 0)
        if q:
            query = query.where(User.username.ilike(f"%{q}"))
        return query

    @staticmethod
    async def delete_user(db: DbSession, user_id: int):
        user_query = select(User).where(User.is_deleted == 0, User.id == user_id)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()
        if not user:
            # 用户不存在或已被删除
            return False
        delete_stmt = update(User).where(User.id == user_id).values(is_deleted=1)
        await db.execute(delete_stmt)
        return True

    @staticmethod
    async def update_user(db, user_data: UpdateUserSchema) -> Tuple[bool, str]:
        """
        修改用户信息
        :param db: 数据库会话
        :param user_data: 包含用户ID和更新信息的对象
        :return: 是否修改成功
        """
        # 1. 检查用户是否存在且未被删除
        user_query = select(User).where(User.is_deleted == 0, User.id == user_data.id)
        result = await db.execute(user_query)
        user = result.scalar_one_or_none()
        if not user:
            return False, "用户被删除"

        # 2. 构建更新的数据字典（排除 None 值，避免覆盖原有数据）
        update_data = user_data.dict(exclude_unset=True)

        # 3. 如果更新了用户名或邮箱，需要检查唯一性
        if "username" in update_data:
            username_exist = await db.execute(
                select(User).where(User.username == update_data["username"], User.id != user_data.id,
                                   User.is_deleted == 0)
            )
            if username_exist.scalar_one_or_none():
                return False, f"用户名 {update_data['username']} 已被占用"

        if "email" in update_data:
            email_exist = await db.execute(
                select(User).where(User.email == update_data["email"], User.id != user_data.id, User.is_deleted == 0)
            )
            if email_exist.scalar_one_or_none():
                return False, f"邮箱 {update_data['username']} 已被占用"

        # 4. 执行更新操作
        update_stmt = (update(User).where(User.id == user_data.id).values(**update_data))
        await db.execute(update_stmt)

        return True, ""

    @staticmethod
    async def get_user_by_id(db: DbSession, user_id: int):
        query = select(User).where(User.is_deleted == 0, User.id == user_id)
        result = await db.execute(query)
        return result.scalar_one_or_none()


user_service = UserService()
