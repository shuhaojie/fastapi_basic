import hashlib
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, Boolean
from src.core.base.models import BaseDBModel
from src.features.project.models import project_viewers


class User(BaseDBModel):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(32), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    nickname = Column(String(50), nullable=True)
    avatar = Column(String(255), nullable=True)
    is_superuser = Column(Boolean, default=False)

    # 与Project的关系
    owned_projects = relationship("Project", back_populates="owner")
    viewable_projects = relationship("Project", secondary=project_viewers, back_populates="viewers")

    # 与Doc的关系
    doc = relationship("Doc", back_populates="owner")

    @staticmethod
    def make_password(raw_password: str) -> str:
        # 简单示例，实际请用 bcrypt/argon2
        return hashlib.sha256(raw_password.encode()).hexdigest()

    def check_password(self, raw_password: str) -> bool:
        return self.hashed_password == self.make_password(raw_password)
