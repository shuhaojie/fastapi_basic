# db.py
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

DATABASE_URL = "mysql+asyncmy://root:805115148@localhost:3306/fastapi_basic"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

from app.users import models  # noqa


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
