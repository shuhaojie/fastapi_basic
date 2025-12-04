from sqlalchemy import select
from src.features.doc.models import Doc


class DocService:

    @staticmethod
    def get_doc_list(q: str):
        query = select(Doc).where(Doc.is_deleted == 0)
        if q:
            query = query.where(Doc.name.ilike(f"%{q}%"))
        return query


doc_service = DocService()
