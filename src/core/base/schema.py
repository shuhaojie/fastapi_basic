from typing import Any, Dict
from pydantic import BaseModel


class BaseSchema(BaseModel):
    code: int
    success: bool
    message: str
    data: Dict[str, Any]