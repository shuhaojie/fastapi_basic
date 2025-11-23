# src/features/auth/router.py
from sqlalchemy import select
from fastapi import APIRouter, status
from src.dependencies import DbSession
from src.core.base.response import BaseResponse
from src.core.base.schema import BaseSchema
from src.core.utils.security import get_password_hash
from src.core.utils.logger import logger
from src.features.auth.models import User
from src.features.auth.service import auth_service
from src.features.auth.schema import RegisterInputSchema, EmailSchema
from src.features.auth.utils import email_verify

router = APIRouter()


@router.post("/email",
             response_model=BaseSchema,
             status_code=status.HTTP_201_CREATED,
             summary="发送注册验证码邮件",
             description="向指定邮箱发送验证码邮件，用于注册验证"
             )
async def send_code(email_schema: EmailSchema, db: DbSession):
    try:
        # 检查邮箱是否已存在
        result = await db.execute(select(User).where(User.email == email_schema.email))
        if result.scalar_one_or_none():
            return BaseResponse.error(message="邮箱已注册")
        # 生成验证码
        code = email_verify.generate_code()
        logger.info(f"code:{code}")
        # 发送邮件
        success = await email_verify.send_email(email_schema.email, code)
        if success:
            # 保存验证码到缓存
            await email_verify.save_code(email_schema.email, code)
            logger.info(f"save_code={code}")
            return BaseResponse.created(message="邮件发送成功")
        else:
            return BaseResponse.error(message="邮件发送失败")
    except Exception as e:
        logger.exception(e)
        return BaseResponse.error(message=str(e))


@router.post("/register",
             response_model=BaseSchema,
             status_code=status.HTTP_201_CREATED,
             summary="用户注册",
             description="用户注册接口，验证邮箱验证码后创建账户",
             )
async def register(payload: RegisterInputSchema, db: DbSession):
    # 判断用户名是否存在
    if not auth_service.check_username_exists(db, payload.username):
        return BaseResponse.error(message="用户已注册")
    is_valid, message = await email_verify.verify_code(payload.email, payload.code)
    if not is_valid:
        return BaseResponse.error(message)
    try:
        cleaned_data = payload.get_cleaned_data()
        async with db.begin():  # 自动开启事务
            user = User(
                **cleaned_data,
                hashed_password=User.make_password(payload.password)  # 你自己的加密方法
            )
            db.add(user)
            await db.flush()  # 可选：立即获取 user.id
            # await db.commit() 不需要，begin() 上下文自动 commit
    except Exception as e:
        logger.exception(e)
        await db.rollback()
        return BaseResponse.error(code=500, message="服务器内部错误")
    return BaseResponse.created(message="注册成功")


@router.post("/login")
async def login(db: DbSession):
    # db 自动注入
    return {"msg": "login success"}
