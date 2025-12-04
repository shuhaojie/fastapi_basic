from datetime import datetime
from pydantic import BaseModel, Field, ConfigDict, field_serializer
from typing import Optional, List
from src.core.base.schema import BaseListSchema


class DocListData(BaseModel):
    id: int = Field(..., description="文件id")
    file_name: str = Field(..., description="文件名称")
    status: int = Field(..., description="文档状态：0-排队中, 1-审核中, 2-审核成功, 3-审核失败")
    # 需要转为可序列化的 datetime 类型
    create_time: datetime = Field(..., description="文件上传时间")
    owner_name: str = Field(..., description="项目创建人")
    # todo: 需要根据error表的数据而来
    # error_count: int = Field(..., description="发现问题数")
    project_name: str = Field(..., description="项目名称")

    model_config = ConfigDict(from_attributes=True)

    @field_serializer('create_time')
    def serialize_created_at(self, create_time: datetime, _info):
        """将 datetime 序列化为 ISO 格式字符串"""
        return create_time.isoformat()


class DocListOutputSchema(BaseListSchema[DocListData]):
    pass