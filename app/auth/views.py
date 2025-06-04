from datetime import timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import APIRouter, Depends, HTTPException, status
from app.security import (
    create_access_token,
    create_refresh_token,
    verify_password,
)
from app.db import get_db
from app.auth.schemas import UserLogin, UserRegister
from app.auth.crud import user_exist, create_user

router = APIRouter()


@router.post("/login")
async def login_for_access_token(form_data: UserLogin, db: AsyncSession = Depends(get_db)):
    """登录获取访问令牌和刷新令牌"""
    # 在实际应用中，这里应该查询数据库验证用户
    user = await user_exist(db=db, username=form_data.username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 验证密码
    if not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # 创建访问令牌
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": form_data.username}, expires_delta=access_token_expires
    )

    # 创建刷新令牌
    refresh_token_expires = timedelta(days=7)
    refresh_token = create_refresh_token(
        data={"sub": form_data.username}, expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router.post("/register")
async def register_user(user_data: UserRegister, db: AsyncSession = Depends(get_db)):
    """注册新用户"""
    # 用户是否存在
    existing_user = await user_exist(db=db, username=user_data.username)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    # 创建用户
    user = await create_user(
        db=db,
        username=user_data.username,
        password=user_data.password,
    )

    return {
        "msg": "User registered successfully",
        "user_id": user.id,
        "username": user.username
    }