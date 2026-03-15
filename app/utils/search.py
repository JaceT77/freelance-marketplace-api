from sqlalchemy.sql import Select


def apply_case_insensitive_search(statement: Select, column, term: str | None) -> Select:
    if term and term.strip():
        statement = statement.where(column.ilike(f"%{term.strip()}%"))
    return statement
