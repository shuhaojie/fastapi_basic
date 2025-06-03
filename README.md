## 1. 环境准备

> 1. fastapi对python版本要求较高，一些旧的版本可能会有问题，这里使用的是Python3.10.9
> 2. 不同版本的fastapi差异很大，这里的版本是fastapi==0.115.12

- 安装fastapi: `pip install fastapi`
- 安装uvicorn: `pip install uvicorn`
- 编写一个最简单的脚本

```python
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Hello": "World"}
```
- 启动服务: `uvicorn main:app --reload`

## 2. 框架结构

### （1）整体结构

```text
.
└── app
    ├── db.py
    ├── main.py
    └── users
        ├── crud.py
        ├── models.py
        ├── schemas.py
        └── views.py
```

### （2）模块作用

- `main.py`：启动框架，连接路由，建立数据库连接

```python
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
```

- `db.py`：定义数据库连接

```python
# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://root:805115148@localhost:3306/fastapi_basic"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
```

- `users/views.py`：定义users的视图函数

```python
from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.users import schemas, crud
from app.db import get_db

router = APIRouter()


@router.post("/users/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


@router.get("/users/", response_model=list[schemas.UserRead])
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db)
```

- `users/models.py`：定义users里的数据表

```python
# models.py
from sqlalchemy import Column, Integer, String
from app.db import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50))
    email = Column(String(100), unique=True, index=True)
```

- `users/crud.py`：定义users的crud操作

```bash
# crud.py
from sqlalchemy.orm import Session
from app.users import models
from app.users import schemas


def create_user(db: Session, user: schemas.UserCreate):
    db_user = models.User(name=user.name, email=user.email)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_users(db: Session):
    return db.query(models.User).all()
```

- `users/schemas`：对users的视图函数的输入输出定义数据格式

```python
# schemas.py
from pydantic import BaseModel


class UserCreate(BaseModel):
    name: str
    email: str


class UserRead(UserCreate):
    id: int

    class Config:
        orm_mode = True
```

## 3. fastapi使用mysql

### （1）建立连接

### （2）数据迁移

使用的是alembic来做迁移，这里注意要在`db.py`导入模型，不然迁移的时候找不到

```python
from app.users import models  # noqa
```





## 4. pydantic



## 5. 异步

## 

