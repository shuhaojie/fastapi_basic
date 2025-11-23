### 1. 如何组织项目结构

从Django框架迁移到FastAPI框架，最苦恼的事情是FastAPI框架并没有Django startproject这个脚手架工具，因此它的项目结构的组织非常灵活、随意，项目时间长了，就会发现有些结构并不好。

https://github.com/zhanymkanov/fastapi-best-practices 是git上一个star达到了10k以上的项目，里面的项目组织方式是这样的，可以借鉴

```bash
fastapi-project
├── alembic/
├── src
│   ├── auth
│   │   ├── router.py
│   │   ├── schemas.py  # pydantic models
│   │   ├── models.py  # db models
│   │   ├── dependencies.py
│   │   ├── config.py  # local configs
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── aws
│   │   ├── client.py  # client model for external service communication
│   │   ├── schemas.py
│   │   ├── config.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   └── utils.py
│   └── posts
│   │   ├── router.py
│   │   ├── schemas.py
│   │   ├── models.py
│   │   ├── dependencies.py
│   │   ├── constants.py
│   │   ├── exceptions.py
│   │   ├── service.py
│   │   └── utils.py
│   ├── config.py  # global configs
│   ├── models.py  # global models
│   ├── exceptions.py  # global exceptions
│   ├── pagination.py  # global module e.g. pagination
│   ├── database.py  # db connection related stuff
│   └── main.py
├── tests/
│   ├── auth
│   ├── aws
│   └── posts
├── templates/
│   └── index.html
├── requirements
│   ├── base.txt
│   ├── dev.txt
│   └── prod.txt
├── .env
├── .gitignore
├── logging.ini
└── alembic.ini
```

### 2. alembic如何做数据库迁移？

使用alembic迁移，和使用django迁移一样，**并不要求我们启动框架**

#### （1）环境安装

```bash
pip install alembic  # 安装 Alembic
alembic init alembic  # 初始化 Alembic
```

这一步之后，路径下会生成一个`alembic.ini`文件，和一个`alembic`文件夹

#### （2）文件配置

- 修改`.ini`文件，只需要改下面一个配置即可

```ini
# 修改数据库连接, 注意这里如果是异步，也需要使用pymysql!!!
sqlalchemy.url = mysql+pymysql://root:root@localhost:3306/fastapi_basic
```

- 修改`alembic`文件夹的`env.py`

```python
# add your model's MetaData object here
# for 'autogenerate' support
from api.app.base.models import Base
from api.app.user.models import User
target_metadata = Base.metadata
```

#### （3）执行迁移

由于我的ini文件在api下，因此执行迁移需要加如下内容

```bash
alembic -c api/alembic.ini revision --autogenerate -m "Create user table"
```

应用到数据库

```bash
alembic -c api/alembic.ini upgrade head
```



```
以下是老文档，留着备份使用的
```

------------------

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
# run.py
import uvicorn
from fastapi import FastAPI
from db import engine, Base
from api.users.views import router as users_router

app = FastAPI()


# 在启动时建表
@app.on_event("startup")
def startup():
  Base.metadata.create_all(bind=engine)


app.include_router(users_router)

if __name__ == '__main__':
  uvicorn.run(app='main:api', host='0.0.0.0', port=8000, workers=20, reload=True)
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
from api.users import crud
from api.app.users import schemas
from api.db import get_db

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
from api.db import Base


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
from api.users import models
from api.users import schemas


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

### （3）异步版本(重点)

这里在学习到后面的异步之后，发现和之前的同步已经有很大的不同了。特别是在数据库定义模块，非常有必要把有变化的文件再单独给拎出来分析一下

（1）`db.py`：这个文件里改动的代码比较多，但是总结一个要点：**如果要使用异步的数据库操作，必须从头到尾使用异步：包括异步引擎、异步 Session、异步依赖、异步函数，不能和同步部分混用**。

```python
# db.py
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

DATABASE_URL = "mysql+asyncmy://root:pwd@localhost:3306/fastapi_basic"

engine = create_async_engine(DATABASE_URL, echo=False)

AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

from api.users import models  # noqa


async def get_db():
  async with AsyncSessionLocal() as session:
    yield session
```

- DBAPI由`pymysql`变成了`asyncmy`

- `create_engine`变成了`create_async_engine`，创建异步引擎

- `sessionmaker`变成了`async_sessionmaker`，生成异步会话

- 创建会话时，使用了`AsyncSession`，它是一个支持 `await` 的数据库会话

- 重点是最后的，首先是套用了两层async，这是因为
  - 第一层：这个依赖函数是异步的，**所以 FastAPI 会用 `await` 来调用它（注意这句话）**
  - 第二层：创建异步数据库会话，可以先简单理解为这里由于要做I/O操作，因此需要async来修饰
  - 最后的yield：yield和return不同之处在于，它使用于需要打开资源（如数据库连接），然后用完后进行清理（关闭连接、释放资源）

（2）`main.py`：同前面说的，要使用异步，必须全程都使用异步，不能有一处是同步的，这里也要改为异步

```python
# run.py
import uvicorn
from fastapi import FastAPI
from db import engine, Base
from api.users.views import router as users_router

app = FastAPI()


# 在启动时建表
@app.on_event("startup")
async def startup():
  async with engine.begin() as conn:
    await conn.run_sync(Base.metadata.create_all)


app.include_router(users_router)

if __name__ == '__main__':
  uvicorn.run(app='main:api', host='0.0.0.0', port=8000, workers=1, reload=True)
```

- `users/views.py`：同上

```python
import time
import asyncio
import threading
from fastapi import Depends, APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from api.users import crud
from api.app.users import schemas
from api.db import get_db

router = APIRouter()


@router.post("/users/", response_model=schemas.UserRead)
async def create_user(user: schemas.UserCreate, db: AsyncSession = Depends(get_db)):
  return await crud.create_user(db=db, user=user)  # 要使用async+await


@router.get("/users/", response_model=list[schemas.UserRead])
async def read_users(db: AsyncSession = Depends(get_db)):
  return await crud.get_users(db)
```

- `users/crud.py`：这里需要注意的是，在异步里做查询需要用`select`，而不能是之前的`query`

```python
# crud.py
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.users import models
from api.app.users import schemas


async def create_user(db: AsyncSession, user: schemas.UserCreate):
  db_user = models.User(name=user.name, email=user.email)
  db.add(db_user)
  await db.commit()
  await db.refresh(db_user)
  return db_user


async def get_users(db: AsyncSession):
  result = await db.execute(select(models.User))
  return result.scalars().all()
```

## 3. fastapi使用mysql

### （1）建立连接

在入口程序`main.py`中

```python
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
```

在定义连接的`db.py`中

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://root:805115148@localhost:3306/fastapi_basic"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

### （2）Base和SessionLocal

在上面的定义中，有两个关键变量，值得说明一下

**Base**

- **模型定义的基础**：所有数据库模型类都继承自 `Base`，提供将 Python 类映射到数据库表的机制，例如：`class User(Base):`

- **元数据容器**：收集所有继承自它的模型的元数据（表结构信息），包含表名、列定义、索引、约束等信息，可通过 `Base.metadata` 访问这些元数据

- **表创建/删除**：提供创建和删除表的方法：

  ```python
  Base.metadata.create_all(engine)  # 创建所有表
  Base.metadata.drop_all(engine)    # 删除所有表
  ```

- **统一注册点**：自动发现所有继承自 `Base` 的模型，确保所有模型都被正确注册到 SQLAlchemy 的元数据系统中

**SessionLocal**

- **会话创建工厂**：用于创建新的数据库会话对象，每次调用 `SessionLocal()` 都会创建一个新的独立会话
- **配置会话行为**：
  - `autocommit=False`：禁用自动提交，需要显式调用 `commit()`
  - `autoflush=False`：禁用自动刷新，需要显式调用 `flush()`
  - `bind=engine`：指定会话使用的数据库引擎
- **事务管理**：
  - 每个会话代表一个数据库事务
  - 管理对象的添加、修改和删除操作
  - 提供 `commit()` 和 `rollback()` 方法
- **对象状态跟踪**：
  - 跟踪会话中所有对象的状态变化
  - 管理对象的持久化状态（新创建、已修改、待删除等）

### （3）数据迁移

使用的是alembic来做迁移，这里注意要在`db.py`导入模型，不然迁移的时候找不到

```python
from api.users import models  # noqa
```

生成迁移文件

```bash
# 创建初始迁移（第一次使用）
alembic revision --autogenerate -m "Initial migration"

# 后续模型变更后创建新迁移
alembic revision --autogenerate -m "Add new table"
```

应用迁移

```bash
alembic upgrade head
```

## 4. 异步

### （1）同步VS异步

- 同步I/O：当程序遇到I/O操作（如网络请求、文件读写）时，会阻塞当前线程直到操作完成。线程在等待期间什么也不做，浪费了CPU资源。
- 异步I/O：在遇到I/O操作时**立即挂起当前任务**，将控制权交还给事件循环，事件循环可以调度其他任务执行。当I/O操作完成后，再恢复挂起的任务。当一个协程发起网络请求时，**它会`await`并释放CPU**，事件循环会去执行其他协程，而不是傻等。

### （2）核心概念

- **协程 (Coroutine)**：使用 `async def` 定义的函数，**可暂停和恢复执行**
- **事件循环 (Event Loop)**：管理和调度协程执行的引擎
- **可等待对象 (Awaitable)**：可被 `await` 调用的对象（协程、任务、Future）

### （3）async和await

- **async**：

  - 将普通函数转换为协程
  - 调用时不会立即执行，而是返回协程对象

  ```python
  # 定义异步函数
  async def fetch_data():
      # 异步操作
      return "data"
  ```

- **await**：

  - 暂停当前协程，直到等待的操作完成
  - 交出控制权给事件循环，允许其他任务运行
  - 只能用在 async 函数内部

  ```python
  async def process_data():
      # 等待异步操作完成
      result = await fetch_data()
      print(f"Received: {result}")
  ```

### （4）实际应用

这里分别写了一个同步请求和一个异步请求，然后写了一个脚本分别调用100次接口

```python
import threading

@router.get("/async-data")
async def get_async_data():
    print(f"Handling async request in thread: {threading.get_ident()}")
    # 模拟 I/O 操作（如数据库查询）
    await asyncio.sleep(1)
    return {"message": "Async data fetched"}


@router.get("/sync-data")
def get_sync_data():
    print(f"Handling sync request in thread: {threading.get_ident()}")
    # 模拟阻塞操作
    time.sleep(1)
    return {"message": "Sync data fetched"}
```

结果：异步总耗时1.17s，平均耗时0.012s；同步总耗时3.19s，平均耗时0.032s。

### （5）异步核心原理

在上面的例子中，有一个非常重要的点，异步里所有**打印的线程id都一样**，这是为什么呢？为什么不使用多线程+协程的形式呢？这就是异步编程模型的核心原理，**Python 的异步编程基于单线程事件循环，所有协程都在同一个主线程中执行**，遇到await时，当前协程暂停，事件循环选择另一个就绪的协程继续执行，所有协程在同一个线程中交替执行。

![image-20250603164944674](docs/image-20250603164944674.png)

为什么使用单线程模型？

- 切换线程，有上下文切换的开销，单线程的话，开销小

- 多线程会占用内存，每个线程所需要消耗的内存大概有100MB左右
- 单线程，没有锁机制

### （6）使用场景

- I/O密集型操作，例如数据库查询

```python
# 异步数据库查询
@app.get("/users/{user_id}")
async def read_user(user_id: int):
    async with AsyncSession() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalars().first()
        return user
```

- 外部api调用

```python
import httpx

@app.get("/external-data")
async def fetch_external_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
```

- 文件操作

```python
import aiofiles

@app.post("/upload")
async def upload_file(file: UploadFile):
    async with aiofiles.open(file.filename, "wb") as buffer:
        while content := await file.read(1024):
            await buffer.write(content)
    return {"filename": file.filename}
```

## 5. 使用日志

使用之前的方案，在启动fastapi框架时，去初始化日志

```python
@app.on_event("startup")
async def startup():
    # 初始化日志
    log_init()
```

定义日志的方法如下：

```python
def log_init():
    logger.setLevel(level=logging.INFO)
    formatter = logging.Formatter(
        '进程ID:%(process)d - '
        '线程ID:%(thread)d- '
        '日志时间:%(asctime)s - '
        '代码路径:%(pathname)s:%(lineno)d - '
        '日志等级:%(levelname)s - '
        '日志信息:%(message)s'
    )
    logger.handlers.clear()
    # 设置api log存储
    api_handler = handlers.TimedRotatingFileHandler(os.path.join(log_dir, "logs/api.log"), encoding='utf-8', when='W6')
    api_handler.setLevel(level=logging.INFO)
    api_handler.setFormatter(formatter)
    logger.addHandler(api_handler)
```

## 6. 权限认证

FastAPI的权限认证没有Django封装得那么好，它的方法参考

```python
@router.get("/protected")
async def protected_route(current_user: dict = Depends(get_current_user)):
    logger.info(current_user)
    return {"msg": f"Hello {current_user['username']}!"}
```

这里`Depends`的作用：FastAPI 会**先执行** `get_current_user()` 函数，而不是直接执行 `protected_route`，如果 `get_current_user()` 成功返回用户数据（如 `{"id": 1, "username": "john"}`），这个返回值会被自动赋值给 `current_user` 参数，然后路由函数才继续执行。

这里的`get_current_user`是用来校验token是否合法的

```python
async def get_current_user(token: str = Depends(oauth2_scheme)):
    """获取当前认证用户"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "access":
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    # 在实际应用中，这里应该查询数据库获取用户信息
    # 示例中简化处理
    user = {"username": username}
    if not user:
        raise credentials_exception
    return user
```

## 7. 用户集成

