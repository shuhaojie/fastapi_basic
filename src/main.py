from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from sqlalchemy import select, func

from src.common.utils.logger import logger
from src.core.conf.config import settings
from src.core.server.database import AsyncSessionLocal
from src.features.auth.router import router as auth_router
from src.features.user.router import router as user_router
from src.features.project.router import router as project_router
from src.features.doc.router import router as doc_router
from src.core.base.exceptions import register_exception_handlers
from src.common.scripts.initial_data import init_database
from src.features.user.models import Role


async def check_and_init_database():
    """检查并初始化数据库"""
    try:
        logger.info("检查数据库初始化状态...")

        # 创建独立的数据库会话
        async with AsyncSessionLocal() as db:
            # 检查是否已初始化（检查角色表是否有数据）
            result = await db.execute(select(func.count(Role.id)))
            role_count = result.scalar()

            if role_count == 0:
                logger.info("检测到空数据库，开始初始化基础数据...")
                await init_database(db)
                logger.info("数据库初始化完成")
            else:
                logger.info("数据库已初始化，跳过初始化步骤")

    except Exception as e:
        logger.error(f"数据库初始化失败: {e}")
        # 不要抛出异常，以免阻止应用启动
        # 可以考虑记录详细日志或发送告警


@asynccontextmanager
async def lifespan(app: FastAPI):
    """应用生命周期管理（FastAPI 2.2+）"""
    # 启动时
    await check_and_init_database()
    yield
    # 关闭时（可以在这里清理资源）
    logger.info("应用关闭中...")


def create_app() -> FastAPI:
    logger.info("Application create")
    _app = FastAPI(
        debug=settings.DEBUG,
        dependencies=[],
        lifespan=lifespan  # 添加lifespan参数，用于应用启动时初始化数据库
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
    _app.include_router(project_router, prefix="/api/v1/project", tags=["项目"])
    _app.include_router(doc_router, prefix="/api/v1/doc", tags=["文件"])
    register_exception_handlers(_app)
    return _app


app = create_app()

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.main:app",  # 注意这里是字符串，不能写 app
        host="0.0.0.0",
        port=settings.PORT,
        reload=not settings.DEBUG,  # 开发时开
        log_level=settings.LOG_LEVEL,
    )
