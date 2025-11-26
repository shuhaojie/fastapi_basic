from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Optional
from src.core.base.schema import BaseListSchema
from src.core.base.schema import BaseSchema


class DeleteUserSchema(BaseModel):
    id: int


class UpdateUserSchema(BaseModel):
    """修改用户的请求模型"""
    id: int = Field(..., description="用户ID")
    username: Optional[str] = Field(None, min_length=3, max_length=32, description="用户名")
    email: Optional[str] = Field(None, description="邮箱")
    nickname: Optional[str] = Field(None, max_length=50, description="昵称")
    avatar: Optional[str] = Field(None, description="头像URL")
    is_superuser: Optional[bool] = Field(None, description="是否为超级管理员")

    class Config:
        schema_extra = {
            "example": {
                "id": 1,
                "username": "new_username",
                "email": "new_email@example.com",
                "nickname": "新昵称",
                "is_superuser": False
            }
        }


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


class UserDetailData(BaseModel):
    id: int = Field(...)
    username: str = Field(...)
    email: str = Field(...)
    nickname: Optional[str] = Field(None)
    avatar: Optional[str] = Field(None)
    is_superuser: bool = Field(...)
    create_time: datetime = Field(...)

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('create_time')
    def serialize_create_time(self, create_time: datetime, _info):
        return create_time.isoformat()


class UserDetailOutputSchema(BaseSchema):
    data: UserDetailData
