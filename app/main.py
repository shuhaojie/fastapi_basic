# main.py
import uvicorn
from fastapi import FastAPI
from db import engine, Base
from app.users.views import router as users_router
app = FastAPI()


# 在启动时建表
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)


app.include_router(users_router)

if __name__ == '__main__':
    uvicorn.run(app='main:app', host='0.0.0.0', port=8000, workers=20, reload=True)
