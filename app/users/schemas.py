from pydantic import BaseModel


class UserCreate(BaseModel):
    username: str
    email: str


class UserRead(UserCreate):
    id: int

    class Config:
        from_attributes = True
