from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Optional, List
from src.core.base.schema import BaseListSchema


# 用户信息模型，用于展示在viewers列表中
class UserBriefInfo(BaseModel):
    id: int = Field(..., description="用户ID")
    username: str = Field(..., description="用户名")
    nickname: Optional[str] = Field(None, description="昵称")

    model_config = ConfigDict(from_attributes=True)


class ProjectListData(BaseModel):
    id: int = Field(..., description="项目ID")
    name: str = Field(..., description="项目名称")
    create_time: datetime = Field(..., description="项目创建时间")
    project_type: int = Field(..., description="公开项目-1, 私有项目-0")
    owner_id: int = Field(..., description="项目创建人ID")
    viewers: List[UserBriefInfo] = Field(..., description="可见用户列表")
    document_count: int = Field(..., description="文件数量")

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('create_time')
    def serialize_created_at(self, create_time: datetime, _info):
        """将 datetime 序列化为 ISO 格式字符串"""
        return create_time.isoformat()


class ProjectListOutputSchema(BaseListSchema[ProjectListData]):
    pass


class CreateProjectInputSchema(BaseModel):
    name: str = Field(..., min_length=1, max_length=32, description="项目名称")
    viewers: list[int] = Field(..., min_length=1, description="可见用户ID列表")
    project_type: int = Field(1, ge=0, le=1, description="项目类型：0-私有项目, 1-公开项目")

    model_config = ConfigDict(from_attributes=True)
