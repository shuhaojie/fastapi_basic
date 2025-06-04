# models.py
from app.base import ORMBaseModel
from sqlalchemy import Column, String


class AuthUser(ORMBaseModel):
    __tablename__ = "auth_user"
    username: str = Column(String(50))
    hashed_password: str = Column(String(100))

    # 可选：添加构造函数以明确接受的参数
    def __init__(self, username: str, hashed_password: str, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.hashed_password = hashed_password
