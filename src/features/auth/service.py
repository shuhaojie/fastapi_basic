from typing import Union
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.features.user.models import User


class AuthService:

    @staticmethod
    async def check_username_exists(db: AsyncSession, username: str) -> bool:
        """检查用户名是否存在"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def check_email_exists(db: AsyncSession, email: str) -> bool:
        """检查用户名是否存在"""
        result = await db.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def get_user_by_account(db: AsyncSession, username: str) -> Union[User, None]:
        """
        根据用户名或邮箱查找用户
        """
        # 先尝试按用户名查找
        user = await db.execute(select(User).where(User.username == username))
        if user:
            return user.scalar_one_or_none()
        else:
            return None


auth_service = AuthService()
