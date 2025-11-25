from typing import Generic, TypeVar, Any, List
from pydantic import BaseModel, Field, ConfigDict

T = TypeVar("T")


class BaseSchema(BaseModel):
    code: int
    success: bool
    message: str


# POST请求无需数据返回的基类
class BaseResponseSchema(BaseSchema):
    data: Any = None


class BaseItemSchema(BaseModel, Generic[T]):
    list: List[T] = Field(..., description="数据列表")
    total: int = Field(..., description="总记录数")
    page_num: int = Field(..., description="当前页码")
    page_size: int = Field(..., description="每页大小")
    total_page: int = Field(..., description="总页码数")

    model_config = ConfigDict(arbitrary_types_allowed=True)


# GET请求需要分页的基类
class BaseListSchema(BaseSchema, Generic[T]):
    data: BaseItemSchema[T] = Field(..., description="分页数据")

    model_config = ConfigDict(arbitrary_types_allowed=True)


# GET请求传参数的基类
class BaseRequestSchema(BaseModel):
    page_num: int = 1
    page_size: int = 10
    q: str | None = None
