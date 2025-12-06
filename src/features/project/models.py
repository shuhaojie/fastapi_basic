import enum
from sqlalchemy import Column, Integer, String, ForeignKey, text, Enum, select, Table, DateTime, Boolean
from sqlalchemy.orm import relationship, column_property
from sqlalchemy.sql import func
from src.core.base.models import BaseDBModel

# 创建多对多关系的关联表
project_viewers = Table(
    'project_viewers',
    BaseDBModel.metadata,  # 注意这里不能使用Base.metadata
    Column('id', Integer, primary_key=True, index=True, autoincrement=True),
    Column('project_id', Integer, ForeignKey('project.id')),
    Column('user_id', Integer, ForeignKey('user.id')),
    Column('create_time', DateTime, default=func.now(), nullable=False),
    Column('update_time', DateTime, default=func.now(),
           onupdate=func.now(), nullable=False),
    Column('is_deleted', Boolean, default=False, nullable=False)
)


class ProjectType(enum.IntEnum):
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

    project_type = Column(
        Integer,
        Enum(ProjectType), 
        default=ProjectType.PUBLIC.value, 
        comment="0-私有项目, 1-公开项目"
        )

    # 与Doc的关系
    doc = relationship("Doc", back_populates="project")

    # 高级写法, 好好学习
    document_count = column_property(
        select(func.count(1))
        .select_from(text("doc"))
        .where(text("doc.project_id = project.id"))
        .scalar_subquery()
    )

    def __repr__(self):
        return f"<Project(name='{self.name}')>"
