from typing import Annotated
from fastapi import Depends, HTTPException, Header, status
from src.database import AsyncSession, get_db
from src.core.utils.logger import logger

# 数据库依赖（最常用）
DbSession = Annotated[AsyncSession, Depends(get_db)]


# 可选：统一的 X-Request-ID 追踪
async def get_request_id(x_request_id: str | None = Header(default=None, alias="X-Request-ID")):
    if not x_request_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="X-Request-ID header is missing",
        )
    logger.info(f"Request ID: {x_request_id}")
    return x_request_id