from env import env
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, DateTime, Boolean, func

DATABASE_URL = f"mysql+aiomysql://{env.MYSQL_USER}:{env.MYSQL_PASSWD}@{env.MYSQL_HOST}:{env.MYSQL_PORT}/{env.MYSQL_DB}"

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class BaseModel(Base):
    __abstract__ = True  # 不要单独创建表

    create_time = Column(DateTime, default=func.now(), nullable=False)
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)