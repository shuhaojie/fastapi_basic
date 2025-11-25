import traceback
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException
from src.common.utils.logger import logger


def json_response(message: str, code: int, status: int):
    return JSONResponse(
        status_code=status,
        content={
            "success": False,
            "message": message,
            "data": None,
            "code": code
        }
    )


# -------------------------
# 1. FastAPI 全局 404 处理
# -------------------------
async def not_found_handler(request: Request, exc: StarletteHTTPException):
    logger.warning(f"404 Not Found: {request.method} {request.url.path}")
    return json_response("请求的接口不存在", 404, 404)


# -------------------------
# 2. FastAPI 全局 500 处理
# -------------------------
async def internal_error_handler(request: Request, exc: Exception):
    logger.error(
        f"500 Error: {request.method} {request.url.path}\n"
        f"{traceback.format_exc()}"
    )
    return json_response("服务器内部错误", 500, 500)


# -------------------------
# 注册所有异常处理器
# -------------------------
def register_exception_handlers(app: FastAPI):

    # 由于注册了这个，那么所有 404、405、500（FastAPI 内部抛的）都会先走这里
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request: Request, exc: StarletteHTTPException):
        if exc.status_code == 404:
            return await not_found_handler(request, exc)
        # 对于其他 HTTPException，你如果想自定义，也可以统一处理
        return JSONResponse(
            status_code=exc.status_code,
            content={
                "success": False,
                "message": exc.detail,
                "data": None,
                "code": exc.status_code
            }
        )

    # 如果上面的装饰器找不到，再查找父类异常Exception
    @app.exception_handler(Exception)
    async def all_exception_handler(request: Request, exc: Exception):
        return await internal_error_handler(request, exc)
