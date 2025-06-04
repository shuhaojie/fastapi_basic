from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models import AuthUser
from app.security import get_password_hash


async def user_exist(db: AsyncSession, username: str):
    result = await db.execute(select(AuthUser).where(AuthUser.username==username))
    return result.scalars().first()


async def create_user(db: AsyncSession, username: str, password: str):
    hashed_password = get_password_hash(password)
    user = AuthUser(username=username, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
