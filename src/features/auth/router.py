from fastapi import APIRouter, status
from datetime import timedelta
from src.core.server.dependencies import DbSession
from src.core.conf.config import settings
from src.core.base.response import BaseResponse
from src.core.base.schema import BaseResponseSchema
from src.common.utils.logger import logger
from src.common.utils.security import create_access_token, create_refresh_token
from src.features.auth.models import User
from src.features.auth.service import auth_service
from src.features.auth.schema import RegisterInputSchema, EmailSchema, LoginInputSchema, LoginOutputSchema, LoginData
from src.features.auth.utils import email_verify

router = APIRouter()


@router.post("/email",
             response_model=BaseResponseSchema,
             status_code=status.HTTP_201_CREATED,
             summary="发送注册验证码邮件",
             description="向指定邮箱发送验证码邮件，用于注册验证"
             )
async def send_code(email_schema: EmailSchema, db: DbSession):
    # 检查邮箱是否已存在
    if not auth_service.check_email_exists(db, email_schema.email):
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


@router.post("/register",
             response_model=BaseResponseSchema,
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
    cleaned_data = payload.get_cleaned_data()
    async with db.begin():  # 自动开启事务
        user = User(
            **cleaned_data,
            hashed_password=User.make_password(payload.password)  # 你自己的加密方法
        )
        db.add(user)
        await db.flush()  # 可选：立即获取 user.id
        # await db.commit() 不需要，begin() 上下文自动 commit
        # await db.rollback() 也不需要, 因为失败会自动回滚
    return BaseResponse.created(message="注册成功")


@router.post("/login",
             response_model=LoginOutputSchema,
             status_code=status.HTTP_200_OK,
             summary="用户登录",
             description="用户登录")
async def login(payload: LoginInputSchema, db: DbSession):
    user = await auth_service.get_user_by_account(db, payload.username)
    if not user:
        return BaseResponse.error("用户不存在")
    if not user.check_password(payload.password):
        return BaseResponse.error("密码错误")

    # 2. 准备 token 数据
    token_data = {
        "sub": str(user.id),  # 用户ID作为主题
        "username": user.username,
        "email": user.email,
        "is_superuser": user.is_superuser
    }

    # 3. 生成 access_token (短期令牌)
    access_token_expires = timedelta(days=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data=token_data, expires_delta=access_token_expires)

    # 4. 生成 refresh_token (长期令牌，用于获取新的 access_token)
    refresh_token_expires = timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(data=token_data, expires_delta=refresh_token_expires)

    return BaseResponse.success(
        message="登录成功",
        data=LoginData(
            refresh=refresh_token,
            access=access_token,
            is_admin=user.is_superuser
        )
    )
