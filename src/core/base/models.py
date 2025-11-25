from sqlalchemy import Column, DateTime, Boolean, func
from src.core.server.database import Base

class BaseDBModel(Base):
    __abstract__ = True  # 不要单独创建表

    create_time = Column(DateTime, default=func.now(), nullable=False)
    update_time = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False)
    is_deleted = Column(Boolean, default=False, nullable=False)