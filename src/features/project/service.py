from sqlalchemy import select
from src.features.project.models import Project
from src.features.user.models import User
from src.core.server.dependencies import DbSession
from src.features.project.schema import CreateProjectInputSchema


class ProjectService:

    @staticmethod
    def get_project_list(q: str):
        query = select(Project).where(Project.is_deleted == 0)
        if q:
            query = query.where(Project.name.ilike(f"%{q}%"))
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


project_service = ProjectService()
