from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.features.auth.models import User


class AuthService:

    @staticmethod
    async def check_username_exists(db: AsyncSession, username: str) -> bool:
        """检查用户名是否存在"""
        result = await db.execute(
            select(User).where(User.username == username)
        )
        return result.scalar_one_or_none() is not None


auth_service = AuthService()
