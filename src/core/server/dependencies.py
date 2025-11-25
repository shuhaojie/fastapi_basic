from typing import Annotated
import redis.asyncio as redis
from src.core.conf.config import settings
from fastapi import Depends, HTTPException, Header, status
from src.core.server.database import AsyncSession, get_db
from src.common.utils.logger import logger

# 数据库依赖（最常用）
DbSession = Annotated[AsyncSession, Depends(get_db)]

# redis全局连接池（推荐）
_redis_client = None


# 可选：统一的 X-Request-ID 追踪
async def get_request_id(x_request_id: str | None = Header(default=None, alias="X-Request-ID")):
    if not x_request_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Request-ID header is missing",
        )
    logger.info(f"Request ID: {x_request_id}")
    return x_request_id


async def get_redis() -> redis.Redis:
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.from_url(
            # "redis://:yourpassword@127.0.0.1:6379/1"
            f"redis://:{settings.REDIS_PASSWD}@{settings.REDIS_HOST}:{settings.REDIS_PORT}/{settings.REDIS_DB}",
            encoding="utf-8",
            decode_responses=True
        )
    return _redis_client
