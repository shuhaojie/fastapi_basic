import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.common.utils.logger import logger
from src.core.base.response import BaseResponse
from typing import Any, Dict, Optional
from fastapi import status


class MessageException(Exception):
    """自定义消息异常"""

    def __init__(
            self,
            message: str,
            status_code: int = status.HTTP_400_BAD_REQUEST,
            detail: Optional[Any] = None,
            headers: Optional[Dict[str, str]] = None
    ):
        """
        初始化消息异常

        Args:
            message: 错误消息
            status_code: HTTP状态码，默认400
            detail: 详细错误信息
            headers: 响应头信息
        """
        self.message = message
        self.status_code = status_code
        self.detail = detail
        self.headers = headers
        super().__init__(self.message)


# -------------------------
# 1. FastAPI 全局 404 处理
# -------------------------
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"404 Not Found: {request.method} {request.url.path}")
    return BaseResponse.not_found()


# -------------------------
# 2. FastAPI 全局 500 处理
# -------------------------
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(
        f"500 Error: {request.method} {request.url.path}\n"
        f"{traceback.format_exc()}"
    )
    return BaseResponse.server_error()


# -------------------------
# 注册所有异常处理器
# -------------------------
def register_exception_handlers(app: FastAPI):
    # 捕获 FastAPI 请求校验错误（Pydantic）, 它和404以及500不一样, 这个是fastapi框架抛的异常
    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        # 从 Pydantic 错误结构中提取 msg
        errors = exc.errors()
        msg = ""
        for error in errors:
            # 如果有原始错误对象，使用原始错误消息
            if "ctx" in error and "error" in error["ctx"]:
                msg += str(error["ctx"]["error"]) + ";"
            else:
                # 否则使用默认的错误消息
                msg += error["msg"] + ";"
        return BaseResponse.unprocessable_entity(msg)

    @app.exception_handler(MessageException)
    async def message_exception_handler(request: Request, exc: MessageException):
        return BaseResponse.error(exc.message, status_code=exc.status_code)

    # 由于注册了这个，那么所有 404、405、500（FastAPI 内部抛的）都会先走这里
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return await not_found_handler(request, exc)
        # 对于其他 HTTPException，你如果想自定义，也可以统一处理
        return BaseResponse.error(message=exc.detail, status_code=exc.status_code)

    # 如果上面的装饰器找不到，再查找父类异常Exception
    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        return await internal_error_handler(request, exc)
