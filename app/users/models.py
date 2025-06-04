# models.py
from sqlalchemy import Column, String
from app.base import ORMBaseModel


class User(ORMBaseModel):
    __tablename__ = "users"

    username: str = Column(String(100))
    email: str = Column(String(100))

    def __init__(self, username: str, email: str, **kwargs):
        super().__init__(**kwargs)
        self.username = username
        self.email = email
