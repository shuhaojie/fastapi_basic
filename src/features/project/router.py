from fastapi import APIRouter, Depends, status
from src.common.utils.pagination import paginate
from src.core.base.response import BaseResponse
from src.core.base.exceptions import MessageException
from src.core.base.schema import BaseRequestSchema, BaseResponseSchema
from src.common.utils.logger import logger
from src.common.utils.security import require_authentication, login_required, get_current_user
from src.core.server.dependencies import DbSession
from src.features.project.schema import ProjectListOutputSchema, ProjectListData, CreateProjectInputSchema
from src.features.project.service import project_service
from src.features.user.service import user_service
from src.features.user.schema import ViewerUserListOutputSchema, ViewerUserItemData
from src.features.project.schema import UpdateProjectViewersInputSchema

router = APIRouter()


@router.get("/viewers",
            response_model=ViewerUserListOutputSchema,
            status_code=status.HTTP_200_OK,
            summary="获取项目可见用户列表",
            description="获取项目可见用户列表（需登录）",
            # require_authentication和admin_required都不需要拿到注入依赖的返回值，因此可以放到路由装饰器中
            dependencies=[Depends(require_authentication), Depends(login_required)],
            )
async def list_viewers(db: DbSession,
                       user=Depends(get_current_user),
                       params: BaseRequestSchema = Depends()):
    """
    获取项目列表接口
    """
    logger.info(f"user_id:{user['sub']}")
    is_superuser = user["is_superuser"]
    if is_superuser:
        query = user_service.get_user_list(q=params.q)  # 管理员的可见用户是所有人
    else:
        # 注意：需要将user["id"]转换为整数
        query = user_service.get_user_list(user_id=int(user["sub"]), q=params.q)  # 非管理员的可见用户只有自己

    # 使用分页函数处理查询
    data = await paginate(db, query, params.page_num, params.page_size)

    # 将查询结果转换为ViewerUserItemData列表
    data["list"] = [ViewerUserItemData.model_validate(item) for item in data["list"]]

    return BaseResponse.success(data=data)


@router.put("/update/viewers/{project_id}",
            response_model=BaseResponseSchema,
            status_code=status.HTTP_200_OK,
            summary="更新项目可见用户列表",
            description="在项目原有可见人员基础上增加或移除用户（需登录）",
            dependencies=[Depends(require_authentication), Depends(login_required)],
            )
async def update_project_viewers(project_id: int,
                                 db: DbSession,
                                 payload: UpdateProjectViewersInputSchema,
                                 user=Depends(get_current_user)):
    """
    更新项目可见用户列表接口
    """
    # 校验项目所有者权限
    if not await project_service.check_project_owner(db, project_id, int(user["sub"])):
        raise MessageException(message="您无权修改此项目的可见人员")

    # 执行更新
    success = await project_service.update_project_viewers(db, project_id, viewer_ids=payload.viewers)

    if success:
        return BaseResponse.success(message="项目可见用户更新成功")
    else:
        return BaseResponse.error(message="项目可见用户更新失败")


@router.post("/create",
             response_model=BaseResponseSchema,
             status_code=status.HTTP_201_CREATED,
             summary="创建项目",
             description="创建项目（需登录）",
             dependencies=[Depends(require_authentication), Depends(login_required)],
             )
async def create_project(db: DbSession,
                         payload: CreateProjectInputSchema,
                         user=Depends(get_current_user)):
    # 验证项目名称是否已存在
    if await project_service.check_project_name_exists(db, payload.name, int(user["sub"])):
        return BaseResponse.error(message="您已创建过同名项目")

    # 创建项目
    project = await project_service.create_project(db, payload, int(user["sub"]))
    if project:
        return BaseResponse.created(message="项目创建成功", data={"project_id": project.id})
    else:
        return BaseResponse.error(message="项目创建失败")


@router.get("/list",
            response_model=ProjectListOutputSchema,
            status_code=status.HTTP_200_OK,
            summary="获取项目列表",
            description="获取项目列表（需登录）",
            # require_authentication和admin_required都不需要拿到注入依赖的返回值，因此可以放到路由装饰器中
            dependencies=[Depends(require_authentication), Depends(login_required)],
            )
async def list_projects(db: DbSession, params: BaseRequestSchema = Depends()):
    """
    获取项目列表接口
    """
    query = project_service.get_project_list(params.q)
    data = await paginate(db, query, params.page_num, params.page_size)
    data["list"] = [ProjectListData.model_validate(item) for item in data["list"]]
    return BaseResponse.success(data=data)
