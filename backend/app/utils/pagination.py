import math

from sqlalchemy import Select, func, select
from sqlalchemy.orm import Session


def paginate(db: Session, stmt: Select, page: int = 1, size: int = 20) -> tuple[list, int, int]:
    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    items = db.scalars(stmt.offset((page - 1) * size).limit(size)).all()
    pages = math.ceil(total / size) if size else 0
    return list(items), total, pages
