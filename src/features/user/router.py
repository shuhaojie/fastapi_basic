from fastapi import APIRouter, status, Depends, Path
from src.features.user.schema import UserDetailOutputSchema, UserDetailData
from src.core.server.dependencies import DbSession
from src.core.base.schema import BaseRequestSchema, BaseResponseSchema
from src.core.base.response import BaseResponse
from src.common.utils.pagination import paginate
from src.common.utils.logger import logger
from src.common.utils.security import verify_token, admin_required
from src.features.user.service import user_service
from src.features.user.schema import UserListOutputSchema, UserListData, DeleteUserSchema, UpdateUserSchema

router = APIRouter()


@router.get("/list",
            response_model=UserListOutputSchema,
            status_code=status.HTTP_200_OK,
            summary="获取系统用户列表",
            description="获取系统中所有用户的列表（仅管理员可操作）"
            )
async def user_list(db: DbSession,
                    params: BaseRequestSchema = Depends(),
                    user=Depends(admin_required),
                    token=Depends(verify_token)
                    ):
    logger.info(f"user:{user}")
    query = user_service.get_user_list(params.q)
    data = await paginate(db, query, params.page_num, params.page_size)
    # 将数据库对象转为普通python格式
    data["list"] = [UserListData.model_validate(item) for item in data["list"]]
    return BaseResponse.success(data=data)


@router.delete("/delete",
               response_model=BaseResponseSchema,
               status_code=status.HTTP_201_CREATED,
               summary="删除用户",
               description="删除用户（仅管理员可操作）"
               )
async def delete_user(db: DbSession,
                      params: DeleteUserSchema = Depends(),
                      user=Depends(admin_required),
                      token=Depends(verify_token)
                      ):
    logger.info(f"user:{user}")
    success = await user_service.delete_user(db, params.id)
    if not success:
        return BaseResponse.error(message=f"用户ID: {params.id} 不存在或已被删除")
    return BaseResponse.success(message="用户删除成功")


@router.put(
    "/update",
    response_model=BaseResponseSchema,
    status_code=status.HTTP_201_CREATED,
    summary="修改用户",
    description="修改用户信息（仅管理员可操作）"
)
async def update_user(db: DbSession,
                      params: UpdateUserSchema = Depends(),
                      user=Depends(admin_required),
                      token=Depends(verify_token)
                      ):
    """
    修改用户信息

    - **id**: 用户ID（必须）
    - **username**: 新用户名（可选）
    - **email**: 新邮箱（可选）
    - **nickname**: 新昵称（可选）
    - **avatar**: 新头像URL（可选）
    - **is_superuser**: 是否为超级管理员（可选）
    """
    logger.info(f"用户 {params.username} 正在修改用户 {params.id}")
    success, message = await user_service.update_user(db, params)
    if not success:
        return BaseResponse.error(message=message)
    return BaseResponse.success(message="用户修改成功")


@router.get(
    "/detail/{id}",
    response_model=UserDetailOutputSchema,
    status_code=status.HTTP_200_OK,
    summary="获取用户详情",
    description="获取指定用户的信息（仅管理员可操作）"
)
async def user_detail(db: DbSession,
                      id: int = Path(..., ge=1),
                      user=Depends(admin_required),
                      token=Depends(verify_token)
                      ):
    logger.info(f"user:{user}")
    item = await user_service.get_user_by_id(db, id)
    if not item:
        return BaseResponse.not_found("用户不存在")
    return BaseResponse.success(data=UserDetailData.from_orm(item))
