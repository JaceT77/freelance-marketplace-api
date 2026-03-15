from fastapi import HTTPException, status
from sqlalchemy.sql import Select


def apply_budget_filters(
    statement: Select,
    column,
    min_budget: float | None,
    max_budget: float | None,
) -> Select:
    if min_budget is not None and max_budget is not None and min_budget > max_budget:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="min_budget cannot be greater than max_budget.",
        )
    if min_budget is not None:
        statement = statement.where(column >= min_budget)
    if max_budget is not None:
        statement = statement.where(column <= max_budget)
    return statement
