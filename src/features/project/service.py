from typing import Set
from sqlalchemy import select, update
from sqlalchemy.orm import selectinload
from datetime import datetime, timezone
from src.features.project.models import Project, project_viewers
from src.features.user.models import User
from src.core.server.dependencies import DbSession
from src.features.project.schema import CreateProjectInputSchema


class ProjectService:

    @staticmethod
    def get_project_list(q: str):
        query = select(Project).where(Project.is_deleted == 0)
        if q:
            query = query.where(Project.name.ilike(f"%{q}%"))
        # 使用selectinload预加载viewers关系，避免在异步环境中访问关系时出现MissingGreenlet错误
        query = query.options(selectinload(Project.viewers))
        return query

    @staticmethod
    async def check_project_name_exists(db: DbSession, name: str, owner_id: int) -> bool:
        """
        检查用户是否已创建同名项目
        """
        query = select(Project).where(
            Project.is_deleted == 0,
            Project.name == name,
            Project.owner_id == owner_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def create_project(db: DbSession, payload: CreateProjectInputSchema, owner_id: int) -> Project:
        users = []
        if payload.viewers:
            result = await db.execute(select(User).where(User.id.in_(payload.viewers)))
            users = result.scalars().all()
        project = Project(
            name=payload.name,
            project_type=payload.project_type,
            owner_id=owner_id,
            # viewer是一个relationship, pycharm会认为这不是一个字段而告警, 加上# type: ignore 来忽略告警
            viewers=users  # type: ignore
        )
        db.add(project)
        await db.flush()  # 获取项目ID
        return project

    @staticmethod
    async def check_project_owner(db: DbSession, project_id: int, user_id: int) -> bool:
        """
        检查指定用户是否为指定项目的所有者
        """
        query = select(Project).where(
            Project.is_deleted == 0,
            Project.id == project_id,
            Project.owner_id == user_id
        )
        result = await db.execute(query)
        return result.scalar_one_or_none() is not None

    @staticmethod
    async def update_project_viewers(db: DbSession, project_id: int, viewer_ids: list[int]) -> Project:
        # 1. 首先查出当前项目有哪些可见用户
        query = select(project_viewers.c.user_id).where(
            (project_viewers.c.project_id == project_id) &
            (project_viewers.c.is_deleted.is_(False))
        )
        result = await db.execute(query)
        current_ids: Set[int] = set(result.scalars().all())
        new_ids: Set[int] = set(viewer_ids or [])  # 防止 None

        to_add = new_ids - current_ids  # 需要新增或恢复的
        to_remove = current_ids - new_ids  # 需要软删除的

        # ====================== 执行新增 / 恢复 ======================
        # 2. 软删除：从有到无
        if to_remove:
            await db.execute(
                update(project_viewers)
                .where(
                    (project_viewers.c.project_id == project_id) &
                    (project_viewers.c.user_id.in_(to_remove)) &
                    (project_viewers.c.is_deleted.is_(False))
                )
                .values(
                    is_deleted=True,
                    update_time=datetime.now(timezone.utc)
                )
            )
        # 3. 新增或恢复：从无到有（优先恢复软删除记录）
        if to_add:
            # 查询这些 user_id 是否已有记录（包括软删除的）
            existing_query = select(
                project_viewers.c.user_id,
                project_viewers.c.is_deleted
            ).where(
                (project_viewers.c.project_id == project_id) &
                (project_viewers.c.user_id.in_(to_add))
            )

            existing_result = (await db.execute(existing_query)).mappings().all()
            existing_dict = {row["user_id"]: row for row in existing_result}

            # 需要恢复的（之前存在但 is_deleted=True）
            to_restore = [uid for uid, row in existing_dict.items() if row["is_deleted"]]

            if to_restore:
                await db.execute(
                    update(project_viewers)
                    .where(
                        (project_viewers.c.project_id == project_id) &
                        (project_viewers.c.user_id.in_(to_restore))
                    )
                    .values(
                        is_deleted=False,
                        update_time=datetime.now(timezone.utc)
                    )
                )

            # 需要新增的（之前完全不存在记录）
            to_insert = list(set(to_add) - set(existing_dict.keys()))

            if to_insert:
                await db.execute(
                    project_viewers.insert(),
                    [
                        {
                            "project_id": project_id,
                            "user_id": uid,
                            "is_deleted": False,
                            "create_time": datetime.now(timezone.utc),
                            "update_time": datetime.now(timezone.utc),
                        }
                        for uid in to_insert
                    ]
                )


project_service = ProjectService()
