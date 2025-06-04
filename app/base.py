from sqlalchemy import Column, DateTime, Boolean, Integer
from datetime import datetime
from app.db import Base


class TimestampMixin:
    """时间戳混合类，提供创建时间和更新时间字段"""
    create_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    update_time = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)


class SoftDeleteMixin:
    """软删除混合类，提供删除标记"""
    is_deleted = Column(Boolean, default=False, nullable=False)


class AuditMixin:
    """审计混合类，提供创建者和更新者信息"""
    created_by = Column(Integer, nullable=True)
    updated_by = Column(Integer, nullable=True)


class ORMBaseModel(Base, TimestampMixin, SoftDeleteMixin, AuditMixin):
    """基础模型类，包含所有公共字段"""
    __abstract__ = True  # 关键：表示这是抽象基类，不会创建对应的表

    id = Column(Integer, primary_key=True, autoincrement=True)

    def to_dict(self):
        """将模型转换为字典"""
        return {c.name: getattr(self, c.name) for c in self.__table__.columns}

    def update(self, **kwargs):
        """更新模型字段"""
        for key, value in kwargs.items():
            if hasattr(self, key):
                setattr(self, key, value)