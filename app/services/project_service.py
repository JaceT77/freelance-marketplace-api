from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.models.enums import ProjectStatus
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate
from app.utils.filters import apply_budget_filters
from app.utils.pagination import Page, paginate_statement
from app.utils.search import apply_case_insensitive_search


def create_project(db: Session, client: User, payload: ProjectCreate) -> Project:
    project = Project(
        title=payload.title,
        description=payload.description,
        budget=payload.budget,
        deadline=payload.deadline,
        status=ProjectStatus.OPEN,
        client_id=client.id,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    return get_project_by_id(db, project.id)


def list_open_projects(
    db: Session,
    *,
    page: int,
    page_size: int,
    search: str | None,
    min_budget: float | None,
    max_budget: float | None,
) -> Page:
    statement = (
        select(Project)
        .options(selectinload(Project.client))
        .where(Project.status == ProjectStatus.OPEN)
        .order_by(Project.created_at.desc())
    )
    statement = apply_case_insensitive_search(statement, Project.title, search)
    statement = apply_budget_filters(statement, Project.budget, min_budget, max_budget)
    return paginate_statement(db, statement, page=page, page_size=page_size)


def get_project_by_id(db: Session, project_id: int) -> Project:
    statement = (
        select(Project)
        .options(selectinload(Project.client), selectinload(Project.contract))
        .where(Project.id == project_id)
    )
    project = db.scalar(statement)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )
    return project


def ensure_project_visibility(project: Project, user: User) -> None:
    if project.status == ProjectStatus.OPEN:
        return
    if project.client_id == user.id:
        return
    if project.contract and project.contract.freelancer_id == user.id:
        return
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="You do not have access to this project.",
    )
