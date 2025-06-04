import time
import asyncio
import threading
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from app.users import schemas, crud
from app.db import get_db
from app.log import logger

router = APIRouter()


@router.post("/add_user/", response_model=schemas.UserRead)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
    logger.info(f"user name:{user.username}")
    return await crud.create_user(db=db, user=user)


@router.get("/get_users/", response_model=list[schemas.UserRead])
async def read_users(db: AsyncSession = Depends(get_db)):
    return await crud.get_users(db)


# 异步路由
@router.get("/async-data")
async def get_async_data():
    print(f"Handling async request in thread: {threading.get_ident()}")
    # 模拟 I/O 操作（如数据库查询）
    await asyncio.sleep(1)
    return {"message": "Async data fetched"}


@router.get("/sync-data")
def get_sync_data():
    print(f"Handling sync request in thread: {threading.get_ident()}")
    # 模拟阻塞操作
    time.sleep(1)
    return {"message": "Sync data fetched"}
