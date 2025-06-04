# models.py
from app.base import ORMBaseModel
from sqlalchemy import Column, String


class AuthUser(ORMBaseModel):
    __tablename__ = "auth_user"
    username = Column(String(50))
    hashed_password = Column(String(100))
