from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.common.utils.logger import logger
from src.core.conf.config import settings
from src.features.auth.router import router as auth_router
from src.features.user.router import router as user_router
from src.core.base.exceptions import register_exception_handlers


def create_app() -> FastAPI:
    logger.info("Application create")
    _app = FastAPI(
        debug=settings.DEBUG,
        dependencies=[],
    )
    # === CORS ===
    _app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # 实际项目请改成具体域名
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    # 路由注册
    _app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
    _app.include_router(user_router, prefix="/api/v1/user", tags=["用户"])
    register_exception_handlers(_app)
    return _app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",  # 注意这里是字符串，不能写 app
        host="0.0.0.0",
        port=settings.PORT,
        reload=not settings.DEBUG,  # 开发时开
        log_level=settings.LOG_LEVEL,
    )
