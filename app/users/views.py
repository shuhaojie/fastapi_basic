from fastapi import Depends, APIRouter
from sqlalchemy.orm import Session
from app.users import schemas, crud
from app.db import get_db

router = APIRouter()


@router.post("/users/", response_model=schemas.UserRead)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    return crud.create_user(db=db, user=user)


@router.get("/users/", response_model=list[schemas.UserRead])
def read_users(db: Session = Depends(get_db)):
    return crud.get_users(db)