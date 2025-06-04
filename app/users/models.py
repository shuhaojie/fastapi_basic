# models.py
from sqlalchemy import Column, String
from app.base import ORMBaseModel


class User(ORMBaseModel):
    __tablename__ = "users"

    username = Column(String(100))
    email = Column(String(100))
