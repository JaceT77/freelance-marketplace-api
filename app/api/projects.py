from fastapi import APIRouter, Query, status

from app.api.deps import CurrentClient, CurrentUser, SessionDep
from app.schemas.project import ProjectCreate, ProjectListResponse, ProjectRead
from app.services.project_service import (
    create_project,
    ensure_project_visibility,
    get_project_by_id,
    list_open_projects,
)


router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("", response_model=ProjectRead, status_code=status.HTTP_201_CREATED)
async def create_project_endpoint(
    payload: ProjectCreate,
    db: SessionDep,
    current_client: CurrentClient,
):
    return await create_project(db, current_client, payload)


@router.get("", response_model=ProjectListResponse)
async def list_projects_endpoint(
    db: SessionDep,
    current_user: CurrentUser,
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=10, ge=1, le=100),
    search: str | None = Query(default=None),
    min_budget: float | None = Query(default=None, ge=0),
    max_budget: float | None = Query(default=None, ge=0),
):
    paginated_projects = await list_open_projects(
        db,
        page=page,
        page_size=page_size,
        search=search,
        min_budget=min_budget,
        max_budget=max_budget,
    )
    return ProjectListResponse(
        items=paginated_projects.items,
        total=paginated_projects.total,
        page=paginated_projects.page,
        page_size=paginated_projects.page_size,
    )


@router.get("/{project_id}", response_model=ProjectRead)
async def get_project_endpoint(
    project_id: int,
    db: SessionDep,
    current_user: CurrentUser,
):
    project = await get_project_by_id(db, project_id)
    ensure_project_visibility(project, current_user)
    return project
