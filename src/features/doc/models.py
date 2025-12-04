import enum
from sqlalchemy import Column, Integer, String, ForeignKey, Enum, select, text
from sqlalchemy.orm import relationship, column_property
from src.core.base.models import BaseDBModel


class DocStatus(enum.IntEnum):
    QUEUEING = 0
    REVIEWING = 1
    REVIEWED = 2
    FAILED = 3


class Doc(BaseDBModel):
    __tablename__ = "doc"

    id = Column(Integer, primary_key=True, index=True)
    file_name = Column(String(255), comment="文档名称", index=True)
    file_uuid = Column(String(255), unique=True, comment="文档唯一标识")

    # 文档所有者, 外键关联users表
    owner = relationship("User", back_populates="doc")
    owner_id = Column(Integer, ForeignKey("user.id"))

    # 文档所属项目, 外键关联projects表
    project = relationship("Project", back_populates="doc")
    project_id = Column(Integer, ForeignKey("project.id"))

    # 文件状态
    status = Column(Integer,
                    Enum(DocStatus),
                    default=DocStatus.QUEUEING.value,
                    comment="文档状态：0-排队中, 1-审核中, 2-审核成功, 3-审核失败")

    project_name = column_property(
        select(text("project.name"))
        .select_from(text("project"))
        .where(text("doc.project_id = project.id"))
        .scalar_subquery()
    )

    owner_name = column_property(
        select(text("user.username"))
        .select_from(text("user"))
        .where(text("doc.owner_id = user.id"))
        .scalar_subquery()
    )
