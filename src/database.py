from typing import AsyncGenerator
from src.config import settings
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine, AsyncSession, AsyncEngine
from sqlalchemy.orm import DeclarativeBase

DATABASE_URL = f"mysql+aiomysql://{settings.MYSQL_USER}:{settings.MYSQL_PASSWD}@{settings.MYSQL_HOST}:{settings.MYSQL_PORT}/{settings.MYSQL_DB}"

engine: AsyncEngine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,  # True 时会打印所有 SQL，开发必开，生产必关
    future=True,  # 开启 SQLAlchemy 2.0 新风格（必须开！旧风格已废弃）
    pool_size=settings.POOL_SIZE,  # 连接池常驻连接数（默认 5，推荐 10~20）
    max_overflow=settings.MAX_OVERFLOW,  # 允许临时额外创建的连接数（默认 10，推荐 10~30）
    pool_pre_ping=True,  # 【强烈建议加上】每次取连接前 ping 一下，防止连接断开
    pool_timeout=30,  # 获取连接超时时间（秒）
    pool_recycle=3600,  # 连接回收时间（秒），MySQL 默认 8 小时断开，建议设 3600
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


# 依赖注入：每次请求一个独立的 session
async def get_db() -> AsyncGenerator[AsyncSession, None]:  # 异步依赖
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
