from typing import cast
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.auth.models import AuthUser
from app.security import get_password_hash


async def user_exist(db: AsyncSession, username: str):
    # 这里有个pycharm报错, 非常烦人, 解决: https://stackoverflow.com/a/76862768/10844937
    stmt = select(AuthUser).where(cast("ColumnElement[bool]", AuthUser.username == username))
    result = await db.execute(stmt)
    return result.scalars().first()


async def create_user(db: AsyncSession, username: str, password: str):
    hashed_password = get_password_hash(password)
    user = AuthUser(username=username, hashed_password=hashed_password)
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user
