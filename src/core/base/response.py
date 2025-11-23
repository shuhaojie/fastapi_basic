from fastapi import status
from fastapi.responses import JSONResponse
from typing import Any, Dict, Optional, Union
from pydantic import BaseModel


class Resp(BaseModel):
    """统一响应体结构（前后端约定）"""
    success: bool = True
    message: str = "操作成功"
    data: Optional[Any] = None
    code: int = status.HTTP_200_OK

    # 可选：加个时间戳、trace_id 等（生产环境常用）
    # timestamp: int = Field(default_factory=lambda: int(time.time()))


class BaseResponse:
    """FastAPI 统一响应封装 - 完全模仿你 Django 那套风格"""

    @staticmethod
    def success(
        data: Any = None,
        message: str = "操作成功",
        status_code: int = status.HTTP_200_OK,
        **extra: Any,
    ) -> JSONResponse:
        body = Resp(success=True, message=message, data=data, code=status_code).model_dump()
        body.update(extra)
        return JSONResponse(content=body, status_code=status_code)

    @staticmethod
    def error(
        message: Union[str, Dict, list] = "操作失败",
        data: Any = None,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        **extra: Any,
    ) -> JSONResponse:
        body = Resp(
            success=False,
            message=message,
            data=data,
            code=status_code,
        ).model_dump()
        body.update(extra)
        return JSONResponse(content=body, status_code=status_code)

    @staticmethod
    def created(data: Any = None, message: str = "创建成功", **extra):
        return BaseResponse.success(data, message, status.HTTP_201_CREATED, **extra)

    @staticmethod
    def id_required(message: str = "未传入id", **extra):
        return BaseResponse.error(message, status_code=status.HTTP_400_BAD_REQUEST, **extra)

    @staticmethod
    def not_found(message: str = "资源不存在", **extra):
        return BaseResponse.error(message, status_code=status.HTTP_404_NOT_FOUND, **extra)

    @staticmethod
    def unauthorized(message: str = "未授权访问", **extra):
        return BaseResponse.error(message, status_code=status.HTTP_401_UNAUTHORIZED, **extra)

    @staticmethod
    def forbidden(message: str = "禁止访问", **extra):
        return BaseResponse.error(message, status_code=status.HTTP_403_FORBIDDEN, **extra)

    @staticmethod
    def bad_request(message: str = "请求参数错误", **extra):
        return BaseResponse.error(message, status_code=status.HTTP_400_BAD_REQUEST, **extra)

    @staticmethod
    def server_error(message: str = "服务器内部错误", **extra):
        return BaseResponse.error(message, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, **extra)

