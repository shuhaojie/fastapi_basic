# db.py
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

DATABASE_URL = "mysql+pymysql://root:805115148@localhost:3306/fastapi_basic"

engine = create_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

from app.users import models  # noqa


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
