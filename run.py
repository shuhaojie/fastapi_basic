import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan():

    # 初始化数据库
    async with engine.begin() as conn:
        # 注意这个是run_sync
        await conn.run_sync(Base.metadata.create_all)

    yield


app = FastAPI(lifespan=lifespan)
app.include_router(users_router, prefix="/user", tags=["user"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])

if __name__ == '__main__':
    uvicorn.run(app='main:api', host='0.0.0.0', port=8000, workers=1, reload=True)
