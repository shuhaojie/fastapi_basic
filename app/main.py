# main.py
import uvicorn
from fastapi import FastAPI
from db import engine, Base
from app.users.views import router as users_router
from app.auth.views import router as auth_router
from app.log import log_init

app = FastAPI()


# 在启动时建表
@app.on_event("startup")
async def startup():
    # 初始化日志
    log_init()

    # 初始化数据库
    async with engine.begin() as conn:
        # 注意这个是run_sync
        await conn.run_sync(Base.metadata.create_all)


app.include_router(users_router, prefix="/user")
app.include_router(auth_router, prefix="/auth")

if __name__ == '__main__':
    uvicorn.run(app='main:app', host='0.0.0.0', port=8000, workers=1, reload=True)
