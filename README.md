## 一、项目结构

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

## 二、fastapi使用mysql

### 1. 建立连接

注意，在后面depends的地方，我们会提到，fastapi和django以及flask不一样，它不需要在启动框架时就建立连接，而是在每个router中通过做依赖注入的方式去建立连接。

在很多fastapi的代码中，我们能看到这一句

```python
@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
```

注意：

（1）创建所有表，注意它不是迁移工具，它是用来建表的，如果表存在（哪怕表结构不一样），它都不会执行

（2）**它并不是用来建立连接的**

（3）生产环境，绝对不要用这个，而是用迁移工具来做迁移

因此，对于我们来说，完全可以把这句话给注释调。

### 2. Base和SessionLocal

在定义连接的`db.py`中

```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://root:805115148@localhost:3306/fastapi_basic"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
```

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

### 3. 数据迁移

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

## 三、异步

### 0. 类比

一家餐厅，只有一个服务员（这就是我们的事件循环 event loop），但这个服务员超级能干、超级快，他绝不傻等。餐厅里有10桌客人（10个协程），每桌都点了菜：

- 炒菜（需要等锅5分钟）
- 煮汤（需要等水开8分钟）
- 烤饼（需要等烤箱10分钟）

如果是普通同步代码（阻塞式）：

1. 接到第1桌的炒菜 → 站在锅边傻等5分钟 → 上菜
2. 再去第2桌煮汤 → 站在那儿傻等8分钟 → 上菜
3. 再去第3桌烤饼 → 傻等10分钟… 

总共要等5 + 8 + 10 = 23分钟才能服务完3桌，效率极低！

如果是异步协程（async/await），就可以这样

| 时间点  | 服务员在做什么                                               |
| ------- | ------------------------------------------------------------ |
| 0秒     | 接到1号桌订单 → 下锅炒菜 → 发现要等5分钟 → 挂起来（await）→ 立刻去干别的 |
| 0秒     | 接到2号桌订单 → 下锅煮汤 → 要等8分钟 → 挂起来 → 继续干活     |
| 0秒     | 接到3号桌订单 → 放进烤箱 → 要等10分钟 → 挂起来               |
| 0~5分钟 | 服务员这段时间可以去擦桌子、收银、招呼新客人（处理其他协程或IO） |
| 5分钟   | 1号桌锅好了！→ 事件循环通知 → 恢复执行 → 上菜                |
| 8分钟   | 2号桌汤开了 → 事件循环通知 → 恢复执行 → 上菜                 |
| 10分钟  | 3号桌烤箱叮一声  → 事件循环通知 → 恢复执行 → 上菜            |

具体的对应关系

| 真实世界              | Python 异步机制                            | 说明                 |
| --------------------- | ------------------------------------------ | -------------------- |
| 超级能干的服务员      | 事件循环（event loop）                     | 只有一个，但永不阻塞 |
| 每一桌客人点的菜      | 一个 async def 协程函数                    | 任务                 |
| “下锅后要等5分钟”     | await asyncio.sleep(5) 或 await 请求网络() | IO等待操作           |
| await 这个等待过程    | 协程挂起，让出控制权                       | 关键！不阻塞事件循环 |
| 锅好了/网络响应回来了 | IO完成，触发回调                           | 事件循环收到信号     |
| 服务员回来继续上菜    | 协程恢复执行（resume）                     | 从await后面继续跑    |

### 1. 同步VS异步

- 同步I/O：当程序遇到I/O操作（如网络请求、文件读写）时，会阻塞当前线程直到操作完成。线程在等待期间什么也不做，浪费了CPU资源。
- 异步I/O：在遇到I/O操作时**立即挂起当前任务**，将控制权交还给事件循环，事件循环可以调度其他任务执行。当I/O操作完成后，再恢复挂起的任务。当一个协程发起网络请求时，**它会`await`并释放CPU**，事件循环会去执行其他协程，而不是傻等。

### 2. 核心概念

#### （1）协程

- 协程 (Coroutine)：使用 `async def` 定义的函数，**可暂停和恢复执行**

#### （2）可等待对象

可等待对象 (Awaitable)：可被 `await` 调用的对象（协程、任务、Future）

#### （3）事件循环

事件循环 (Event Loop)：管理和调度协程执行的引擎。

在FastAPI框架中，FastAPI 本身不直接启动事件循环：FastAPI 是一个 ASGI 框架，它不直接管理事件循环**。事件循环是由 **ASGI 服务器（如 Uvicorn、Hypercorn、Daphne）启动的。

```python
# 这是一个常见的 FastAPI 应用结构
from fastapi import FastAPI

app = FastAPI()  # 这里还没有事件循环！

@app.get("/")
async def read_root():
    return {"Hello": "World"}
```

只有通过`uvicorn`启动框架之后，才会启动事件循环

```python
import uvicorn

if __name__ == "__main__":
    # 这里 Uvicorn 启动了事件循环！
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
```

### 3. async和await

#### （1）代码示例

```python
import asyncio
import threading


# 1. 定义协程函数（用 async def 标记）
async def simple_coroutine_1(name, sleep_time):
    # 2. await 挂起协程，释放事件循环（模拟耗时操作，如网络请求/数据库查询）
    print("协程内部执行了")
    await asyncio.sleep(sleep_time)  # asyncio.sleep 是 Python 内置的异步等待函数
    return f"{name} 完成，等待了 {sleep_time} 秒"


async def simple_coroutine_2(name, sleep_time):
    # 2. await 挂起协程，释放事件循环（模拟耗时操作，如网络请求/数据库查询）
    print("协程内部执行了")
    await asyncio.sleep(sleep_time)  # asyncio.sleep 是 Python 内置的异步等待函数
    return f"{name} 完成，等待了 {sleep_time} 秒"


# 3. 主函数（事件循环的入口，必须也是协程）
async def main():
    # 启动两个协程，让事件循环调度执行
    coroutine1 = simple_coroutine_1("A", 2)
    print(f"type coroutine1:{type(coroutine1)}", f"request id: {threading.get_ident()}")
    result1 = await coroutine1
    print(result1)
    coroutine2 = simple_coroutine_2("B", 3)
    print(f"type coroutine2:{type(coroutine2)}", f"request id: {threading.get_ident()}")
    result2 = await coroutine2  # 协程 A 完成后，再执行协程 B（1秒）
    print(result2)


# 4. 启动事件循环（运行主协程）
if __name__ == "__main__":
    asyncio.run(main())  # 唯一的同步入口，负责启动和关闭事件循环
```

打印结果：

```bash
type coroutine1:<class 'coroutine'> request id: 8384880384
协程内部执行了
A 完成，等待了 2 秒
type coroutine2:<class 'coroutine'> request id: 8384880384
协程内部执行了
B 完成，等待了 3 秒
```

#### （2）async

- 将普通函数转换为协程：打印的`type(coroutine1)`是`<class 'coroutine'> `

- **调用时不会立即执行，而是返回协程对象!**：注意观察上面的返回顺序，并不是先打印【协程内部执行了】

- 一个异步函数，调用的时候，前面必须加await，如果不加，不会报错但会有告警。

  ```bash
  /Users/luoan/workspace/code/fastapi_basic/src/features/auth/router.py:26: RuntimeWarning: coroutine 'AuthService.check_email_exists' was never awaited
    if not auth_service.check_email_exists(db, email_schema.email):
  RuntimeWarning: Enable tracemalloc to get the object allocation traceback
  ```

#### （3）await

- 暂停当前协程，直到等待的操作完成
- 交出控制权给事件循环，允许其他任务运行
- **只能用在async函数内部**
- 调用三方包的时候（特别是数据库），何时该加await？

### 4. 异步核心原理

在上面的例子中，有一个非常重要的点，异步里所有**打印的线程id都一样**，这是为什么呢？为什么不使用多线程+协程的形式呢？这就是异步编程模型的核心原理，**Python 的异步编程基于单线程事件循环，所有协程都在同一个主线程中执行**，遇到await时，当前协程暂停，事件循环选择另一个就绪的协程继续执行，所有协程在同一个线程中交替执行。

![image-20250603164944674](docs/image-20250603164944674.png)

为什么使用单线程模型？

- 切换线程，有上下文切换的开销，单线程的话，开销小

- 多线程会占用内存，每个线程所需要消耗的内存大概有100MB左右
- 单线程，没有锁机制

### 5. 使用场景

#### （1）数据库操作

先看一下定义数据连接的地方，比同步版本复杂了很多

```python
# db.py
from sqlalchemy.orm import declarative_base
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

# DBAPI由pymysql变成了asyncmy
DATABASE_URL = "mysql+asyncmy://root:pwd@localhost:3306/fastapi_basic"

# create_engine变成了create_async_engine，创建异步引擎
engine = create_async_engine(DATABASE_URL, echo=False)

# sessionmaker变成了async_sessionmaker，生成异步会话
AsyncSessionLocal = async_sessionmaker(bind=engine,
                                       # 使用`AsyncSession`，它是一个支持 `await`的数据库会话
                                       class_=AsyncSession, 
                                       expire_on_commit=False)

Base = declarative_base()

from api.users import models  # noqa

"""
重点是最后的，首先是套用了两层async，这是因为
- 第一层：这个依赖函数是异步的
- 第二层：创建异步数据库会话，可以先简单理解为这里由于要做I/O操作，因此需要async来修饰
- 最后的yield：yield和return不同之处在于，它使用于需要打开资源（如数据库连接），然后用完后进行清理（关闭连接、释放资源）
"""
async def get_db():
  async with AsyncSessionLocal() as session:
    yield session
```

实际使用时，在做数据库查询时我们需要使用await来挂起，因为【待补充】

```python
@staticmethod
async def check_email_exists(db: AsyncSession, email: str) -> bool:
    """检查邮箱是否存在"""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none() is not None
```

#### （2）外部api调用

```python
import httpx

@app.get("/external-data")
async def fetch_external_data():
    async with httpx.AsyncClient() as client:
        response = await client.get("https://api.example.com/data")
        return response.json()
```

#### （3）文件操作

```python
import aiofiles

@app.post("/upload")
async def upload_file(file: UploadFile):
    async with aiofiles.open(file.filename, "wb") as buffer:
        while content := await file.read(1024):
            await buffer.write(content)
    return {"filename": file.filename}
```

## 四、pydantic

在fastapi里，pydantic几乎是“灵魂伴侣”，它干的活儿远远不止“校验一下参数”那么简单。

### 1. 参数校验

```python
class UserCreate(BaseModel):
    username: str
    age: int = Field(..., ge=1, le=120)
    email: EmailStr
```

FastAPI 会自动校验格式，类型不对自动返回 422

- 确保 `age` 是数字、在区间内
- 自动校验 email 格式

### 2. 类型转换

例如定义的price是float：

```python
class Item(BaseModel):
    price: float
```

收到：`{"price": "10.99"}`，会自动转为float格式

### 3. 响应模型（输出校验）

```python
@router.get("/user", response_model=UserOut)
async def get_user():
    return {"id": "1", "username": "root"}
```

如果类型不符合，FastAPI 会直接抛错，帮助你保持 API 一致性。这个有个好处：我们给客户或者前端一个接口文档，我们的接口可以严格按文档返回。

### 4. 字段逻辑校验

使用`validator` `field_validator`装饰器，例如下面的校验

```python
from pydantic import field_validator

class User(BaseModel):
    password: str

    @field_validator("password")
    def validate_pwd(cls, v):
        if len(v) < 8:
            raise ValueError("密码至少8位")
        return v
```

### 5. 与数据库模型结合

对于列表页分返回，这个比较常见。schema定义的地方加上`model_config = ConfigDict(from_attributes=True)`

<img src="./docs/image-20251129220153640.png" alt="image-20251129220153640" style="zoom:50%;" />

转换的时候，使用`UserListData.model_validate`，即可以将模型转为列表

<img src="./docs/image-20251129220121748.png" alt="image-20251129220121748" style="zoom:35%;" />

### 6. 环境变量

自动从系统环境、env 文件读取。

```python
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DB_URL: str
    DEBUG: bool = False

    class Config:
        env_file = ".env"

settings = Settings()
```



## 五、依赖注入

### 1. 优点

在我的启动代码中，并没有在启动框架时，就去建立数据库连接，这就是依赖注入的强大。只有在实际处理HTTP请求时，才会解析路由函数中声明的依赖项（如 db: DbSession ）。这意味着在应用启动阶段， get_db() 函数不会被调用，自然也就不会建立数据库连接。

## 六、权限校验

基本代码

```python
def get_current_user(request: Request):
    auth = request.headers.get("Authorization")
    if not auth or not auth.startswith("Bearer "):
        # 注意这里必须抛异常
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token无效或已过期")
    token = auth.split(" ")[1]
    try:
        payload = validate_jwt_token(token)
    except Exception as e:
        logger.exception(e)
        # 注意这里必须抛异常
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="token无效或已过期")
    return payload
  
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    # 在这里验证 token
    if not validate_jwt_token(token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="token无效或已过期",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token
  
def login_required(payload=Depends(get_current_user)):
    return payload

@router.post("/email")
async def send_code(email_schema: EmailSchema,
                    db: DbSession,
                    user=Depends(login_required),
                    token=Depends(verify_token)):
       pass
```



- 第一个depends：确保用户需要登录，传token，不然就会报`login_required`里的错误信息
- 第二个depends：swagger前端页面上，会多一个东西

![image-20251124104427050](./docs/image-20251124104427050.png)

点进去的时候，只需要输入access_token值即可，不需要带前面的Bearer

## 七、sqlalchemy orm

### 1. 如何使用？

注意下面这种形式就是orm

```python
    async def get_user_list(db: AsyncSession):
        """
        根据用户名或邮箱查找用户
        """
        # 先尝试按用户名查找
        query = select(User).where(User.is_deleted == 0)
        result = await db.execute(query)
        users = result.scalar()
        return users
```

这个是sqlalchemy最新的orm风格，而我熟悉的`session.query(User).filter(is_deleted==0)`这种形式，属于旧式风格。

## 八、其他问题

### 1. 如何保证接口按照文档返回？

如果不按照这个返回，就报错？

### 2. 如何做异常兜底？

想实现的目的：

- 不用每个里面都写try..except
- 如果是404，我知道是我的接口的404

```python
# 注册所有异常处理器
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
```

### 3. fastapi如何做分页？

纯手写版，零依赖

```
import math
from fastapi import Query
from sqlalchemy import select, func


async def paginate(
        db,
        query,
        page_num: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=200),

):
    """
    :param db: 查询db
    :param query: 查询语句
    :param page_num: 当前页码数
    :param page_size: 一页总条数
    :return:
    """
    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total_items = (await db.execute(count_query)).scalar()
    total_pages = math.ceil(total_items / page_size) if total_items else 0

    # 数据
    items = await db.execute(
        query.offset((page_num - 1) * page_size).limit(page_size)
    )
    items = items.scalars().all()
    return {
        "list": items,
        "total": total_items,
        "total_pages": total_pages,
        "page_num": page_num,
        "page_size": page_size
    }
```

### 4. 列表页如何只返回我要的字段？

```python
class UserListData(BaseModel):
    username: str = Field(..., description="用户名")
    email: str = Field(..., description="邮箱")
    is_superuser: bool = Field(..., description="是否为管理员")
    create_time: datetime = Field(..., description="注册时间")

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('create_time')
    def serialize_create_time(self, create_time: datetime, _info):
        """将 datetime 序列化为 ISO 格式字符串"""
        return create_time.isoformat()
```

注意：

- 这个字段名称需要和数据库保持一致，不然会报错，例如`is_superuser`不能是`is_admin`
- 这里需要把`create_time`做序列化，不然无法返回

### 5. 如何把数据库对象直接返回为列表

```python
    data = await paginate(db, query, params.page_num, params.page_size)
    # 关键步骤，在上一步拿到的是数据库对象，使用这一步，可以把数据库对象转为普通python类型
    data["list"] = [UserListData.from_orm(item) for item in data["list"]]
```

### 6. get请求如何传query_params?

在正常请求传参数的后面加上depends，注意这里如果不加就算payload了

```python
async def user_list(db: DbSession,
                    params: BaseRequestSchema = Depends(),  # 这里一定要有后面的Depends()
                    user=Depends(admin_required),
                    token=Depends(verify_token)
                    ):
```

### 7. fastapi如何传参逻辑

## 4. 异步

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

