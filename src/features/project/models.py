import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Table, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from src.core.base.models import BaseDBModel


Base = declarative_base()

# 创建多对多关系的关联表
project_viewers = Table(
    'project_viewers',
    Base.metadata,
    Column('project_id', Integer, ForeignKey('project.id')),
    Column('user_id', Integer, ForeignKey('user.id'))
)


class ProjectType(enum.Enum):
    PRIVATE = 0
    PUBLIC = 1


class Project(BaseDBModel):
    __tablename__ = "project"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, comment="项目名称")

    # 所有者外键关系
    owner_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    owner = relationship("User", back_populates="owned_projects")

    # 多对多关系：可见用户
    viewers = relationship("User", secondary=project_viewers, back_populates="viewable_projects")

    project_type = Column(Integer, default=1, comment="0-私有项目, 1-公开项目")

    # 基类字段 (假设的BaseModel字段)
    created_at = Column(DateTime, default=func.now(), nullable=False)
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Integer, default=0, comment="逻辑删除标记")  # 根据你的BaseModel可能需要

    def __repr__(self):
        return f"<Project(name='{self.name}')>"
