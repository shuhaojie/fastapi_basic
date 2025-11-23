# src/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.core.utils.logger import logger
from src.config import settings
from src.features.auth.router import router as auth_router
# from src.features.projects.router import router as project_router
# from src.features.documents.router import router as doc_router

app = FastAPI(
    debug=settings.DEBUG,
)


# === CORS ===
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 实际项目请改成具体域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === 路由注册（以后再多也不怕）===
app.include_router(auth_router, prefix="/api/v1/auth", tags=["认证"])
# app.include_router(project_router, prefix="/api/v1/projects", tags=["项目"])
# app.include_router(doc_router, prefix="/api/v1/docs", tags=["文档"])


# === 事件钩子 ===
@app.on_event("startup")
async def startup_event():
    logger.info("Application startup")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("Application shutdown")


# === 健康检查 ===
@app.get("/health")
async def health_check():
    return {"status": "healthy", "project": settings.PROJECT_NAME}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",          # 注意这里是字符串，不能写 app
        host="0.0.0.0",
        port=settings.PORT,
        reload=not settings.DEBUG,         # 开发时开
        log_level=settings.LOG_LEVEL,
    )