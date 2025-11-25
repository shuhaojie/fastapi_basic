from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from src.core.base.schema import BaseListSchema


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


class UserListOutputSchema(BaseListSchema[UserListData]):
    pass
