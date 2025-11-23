# src/features/auth/router.py
from sqlalchemy import select
from fastapi import APIRouter, status
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType, NameEmail
from src.dependencies import DbSession
from src.core.base.response import BaseResponse
from src.core.base.schema import BaseSchema
from src.core.utils.security import get_password_hash
from src.core.utils.logger import logger
from src.features.auth.models import User
from src.features.auth.schema import UserCreate, UserOut, EmailSchema
from src.features.auth.utils import EmailVerification

router = APIRouter()


@router.post("/email",
             response_model=BaseSchema,
             status_code=status.HTTP_201_CREATED,
             summary="发送注册验证码邮件",
             description="向指定邮箱发送验证码邮件，用于注册验证"
             )
async def simple_send(email_schema: EmailSchema):
    try:
        # 生成验证码
        email_verify = EmailVerification()
        verification_code = email_verify.generate_verification_code()
        logger.info(f"verification_code:{verification_code}")
        # 发送邮件
        success = await email_verify.send_email(email_schema.email, verification_code)
        if success:
            return BaseResponse.created(message="邮件发送成功")
        else:
            return BaseResponse.error(message="邮件发送失败")
    except Exception as e:
        logger.exception(e)
        return BaseResponse.error(message=str(e))


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def register(user_data: UserCreate, db: DbSession):
    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == user_data.email))
    if result.scalar_one_or_none():
        return BaseResponse.error(message="邮箱已注册")
    is_valid, message = EmailVerification.verify_code(user_data.email, verification_code)
    # 创建用户
    hashed_password = get_password_hash(user_data.password)
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        nickname=user_data.nickname or user_data.email.split("@")[0]
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.post("/login")
async def login(db: DbSession):
    # db 自动注入
    return {"msg": "login success"}
