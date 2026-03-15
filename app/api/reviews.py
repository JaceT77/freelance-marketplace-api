from fastapi import APIRouter, status

from app.api.deps import CurrentClient, SessionDep
from app.schemas.review import ReviewCreate, ReviewRead
from app.services.review_service import create_review


router = APIRouter(tags=["Reviews"])


@router.post(
    "/contracts/{contract_id}/reviews",
    response_model=ReviewRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_review_endpoint(
    contract_id: int,
    payload: ReviewCreate,
    db: SessionDep,
    current_client: CurrentClient,
):
    return await create_review(
        db,
        contract_id=contract_id,
        client=current_client,
        payload=payload,
    )
