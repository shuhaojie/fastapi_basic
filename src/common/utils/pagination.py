# utils/pagination.py （纯手写版，零依赖）
import math
from fastapi import Query
from sqlalchemy import select, func


async def paginate(
        db,
        query,
        page_num: int = Query(1, ge=1),
        page_size: int = Query(10, ge=1, le=200),

):
    """
    :param db: 查询db
    :param query: 查询语句
    :param page_num: 当前页码数
    :param page_size: 一页总条数
    :return:
    """
    # 总数
    count_query = select(func.count()).select_from(query.subquery())
    total_items = (await db.execute(count_query)).scalar()
    total_pages = math.ceil(total_items / page_size) if total_items else 0

    # 数据
    items = await db.execute(
        query.offset((page_num - 1) * page_size).limit(page_size)
    )
    items = items.scalars().all()
    return {
        "list": items,
        "total": total_items,
        "total_pages": total_pages,
        "page_num": page_num,
        "page_size": page_size
    }
