import uuid
from sqlalchemy import String, Column
from collections.abc import AsyncGenerator
from fastapi import Depends
from fastapi_users.db import SQLAlchemyBaseUserTableUUID, SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from api.app.base.models import Base, BaseModel, engine, async_session_maker


class User(SQLAlchemyBaseUserTableUUID, BaseModel, Base):
    __tablename__ = "user"
    # 重写 id 字段 → 避免 fastapi-users 的自定义 GUID 类型导致 alembic 不兼容
    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = Column(String(64), unique=True)


async def create_db_and_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_user_db(session: AsyncSession = Depends(get_async_session)):
    yield SQLAlchemyUserDatabase(session, User)
