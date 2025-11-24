from typing import Generic, TypeVar, Dict, Any
from pydantic import BaseModel

T = TypeVar("T")


class BaseSchema(BaseModel):
    code: int
    success: bool
    message: str


class BaseResponseSchema(BaseSchema):
    data: Any = None
