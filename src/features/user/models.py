import hashlib
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from sqlalchemy import Column, Integer, String, Boolean, Table, ForeignKey, DateTime
from src.core.base.models import BaseDBModel
from src.features.project.models import project_viewers


# User和Group的多对多关系中间表
user_groups = Table(
    'user_groups',
    BaseDBModel.metadata,  # 注意这里不能使用Base.metadata
    Column('id', Integer, primary_key=True, index=True, autoincrement=True),
    Column('group_id', Integer, ForeignKey('group.id'), nullable=False),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
    Column('create_time', DateTime, default=func.now(), nullable=False),
    Column('update_time', DateTime, default=func.now(),
           onupdate=func.now(), nullable=False),
    Column('is_deleted', Boolean, default=False, nullable=False)
)

# User和Role的多对多关系中间表
user_roles = Table(
    'user_roles',
    BaseDBModel.metadata,
    Column('id', Integer, primary_key=True, index=True, autoincrement=True),
    Column('user_id', Integer, ForeignKey('user.id'), nullable=False),
    Column('role_id', Integer, ForeignKey('role.id'), nullable=False),
    Column('create_time', DateTime, default=func.now(), nullable=False),
    Column('update_time', DateTime, default=func.now(),
           onupdate=func.now(), nullable=False),
    Column('is_deleted', Boolean, default=False, nullable=False)
)


class User(BaseDBModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=True)
    avatar = Column(String(255), nullable=True)

    # 与Project的拥有者关系
    owned_projects = relationship("Project", back_populates="owner")

    # 与Project的者关系
    viewable_projects = relationship("Project", secondary=project_viewers, back_populates="viewers")

    # 与Doc的关系
    doc = relationship("Doc", back_populates="owner")

    # 与Group的关系 - 多对多
    groups = relationship("Group", secondary=user_groups, back_populates="users")
    
    # 与Role的关系 - 多对多
    roles = relationship("Role", secondary=user_roles, back_populates="users")
    

    @staticmethod
    def make_password(raw_password: str) -> str:
        # 简单示例，实际请用 bcrypt/argon2
        return hashlib.sha256(raw_password.encode()).hexdigest()

    def check_password(self, raw_password: str) -> bool:
        return self.hashed_password == self.make_password(raw_password)


class Group(BaseDBModel):
    __tablename__ = "group"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    # 与User的关系 - 多对多
    users = relationship("User", secondary=user_groups, back_populates="groups")


class Role(BaseDBModel):
    __tablename__ = "role"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    description = Column(String(255), nullable=True)

    # 与User的关系 - 多对多
    users = relationship("User", secondary=user_roles, back_populates="roles")