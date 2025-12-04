from fastapi import APIRouter, Depends, status
from src.common.utils.pagination import paginate
from src.common.utils.security import require_authentication, login_required
from src.core.server.dependencies import DbSession
from src.core.base.response import BaseResponse
from src.core.base.schema import BaseRequestSchema
from src.features.doc.schema import DocListOutputSchema, DocListData
from src.features.doc.service import doc_service

router = APIRouter()


@router.get("/list",
            response_model=DocListOutputSchema,
            status_code=status.HTTP_200_OK,
            summary="获取文件列表",
            description="获取文件列表（需登录）",
            # require_authentication和admin_required都不需要拿到注入依赖的返回值，因此可以放到路由装饰器中
            dependencies=[Depends(require_authentication), Depends(login_required)],
            )
async def list_docs(db: DbSession, params: BaseRequestSchema = Depends()):
    """
    获取项目列表接口
    """
    query = doc_service.get_doc_list(params.q)
    data = await paginate(db, query, params.page_num, params.page_size)
    data["list"] = [DocListData.model_validate(item) for item in data["list"]]
    return BaseResponse.success(data=data)
