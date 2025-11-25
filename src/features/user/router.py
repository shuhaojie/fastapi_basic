from fastapi import APIRouter, status, Depends
from src.dependencies import DbSession
from src.core.base.schema import BaseRequestSchema
from src.core.base.response import BaseResponse
from src.core.utils.pagination import paginate
from src.core.utils.logger import logger
from src.core.utils.security import verify_token, admin_required
from src.features.user.service import user_service
from src.features.user.schema import UserListOutputSchema, UserListData

router = APIRouter()


@router.get("/list",
            response_model=UserListOutputSchema,
            status_code=status.HTTP_200_OK,
            summary="获取系统用户列表",
            description="获取系统中所有用户的列表，包含id和username等信息"
            )
async def user_list(db: DbSession,
                    params: BaseRequestSchema = Depends(),
                    user=Depends(admin_required),
                    token=Depends(verify_token)
                    ):
    logger.info(f"user:{user}")
    query = user_service.get_user_list(params.q)
    data = await paginate(db, query, UserListData, params.page_num, params.page_size)
    return BaseResponse.success(data=data)
