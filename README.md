## 1. 环境准备

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



## 3. pydantic

## 4. 异步