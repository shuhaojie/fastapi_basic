from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.features.user.models import User, Role, user_roles
from src.common.utils.logger import logger
from src.core.conf.config import settings


# 1. 获取敏感值（正确方式）
def get_admin_password():
    """获取管理员密码"""
    # 使用 get_secret_value() 方法获取实际值
    return settings.ADMIN_PASSWORD.get_secret_value()


async def init_database(db: AsyncSession):
    """初始化基础数据，使用事务确保原子性"""
    try:
        logger.info("开始初始化数据库...")

        # 1. 初始化角色表
        roles_data = [
            {"name": "普通用户", "description": "普通用户角色"},
            {"name": "管理员", "description": "系统管理员角色"},
        ]

        roles_map = {}
        for role_data in roles_data:
            # 检查是否已存在
            existing = await db.execute(
                select(Role).where(Role.name == role_data["name"])
            )
            existing_role = existing.scalar_one_or_none()

            if existing_role is None:
                new_role = Role(**role_data)
                db.add(new_role)
                await db.flush()  # 获取ID
                roles_map[role_data["name"]] = new_role.id
                logger.info(f"创建角色: {role_data['name']}")
            else:
                roles_map[role_data["name"]] = existing_role.id
                logger.info(f"角色已存在: {role_data['name']}")

        # 2. 初始化admin用户
        admin_user = await db.execute(
            select(User).where(User.username == "admin")
        )
        admin_user = admin_user.scalar_one_or_none()

        if admin_user is None:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=User.make_password(get_admin_password()),  # 使用您的加密方法
                nickname="系统管理员",
            )
            db.add(admin_user)
            await db.flush()  # 获取用户ID
            logger.info("创建管理员用户: admin")
        else:
            logger.info("管理员用户已存在")

        # 3. 关联用户和角色（管理员角色）
        if admin_user.id and "管理员" in roles_map:
            # 检查关联是否已存在
            existing_link = await db.execute(
                select(user_roles).where(
                    user_roles.c.user_id == admin_user.id,
                    user_roles.c.role_id == roles_map["管理员"]
                )
            )
            existing_link = existing_link.first()

            if existing_link is None:
                # 直接使用insert语句，避免ORM延迟问题
                await db.execute(
                    user_roles.insert().values(
                        user_id=admin_user.id,
                        role_id=roles_map["管理员"],
                        is_deleted=False,
                        create_time=datetime.now(),
                        update_time=datetime.now()
                    )
                )
                logger.info("关联用户和角色成功")
            else:
                logger.info("用户角色关联已存在")

        # 提交所有更改
        await db.commit()
        logger.info("数据库初始化成功")

    except Exception as e:
        # 回滚事务
        await db.rollback()
        logger.exception(f"数据库初始化失败: {str(e)}")
        import traceback
        traceback.print_exc()
        raise
