from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.orm import Session
from sqlalchemy.sql import Select


@dataclass
class Page:
    items: list
    total: int
    page: int
    page_size: int


def paginate_statement(
    db: Session,
    statement: Select,
    *,
    page: int,
    page_size: int,
) -> Page:
    total = db.scalar(
        select(func.count()).select_from(statement.order_by(None).subquery())
    ) or 0
    items = db.scalars(
        statement.offset((page - 1) * page_size).limit(page_size)
    ).all()
    return Page(items=items, total=total, page=page, page_size=page_size)
