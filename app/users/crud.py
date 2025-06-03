# crud.py
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.users import models
from app.users import schemas


async def create_user(db: AsyncSession, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


async def get_users(db: AsyncSession):
    result = await db.execute(select(models.User))
    return result.scalars().all()
