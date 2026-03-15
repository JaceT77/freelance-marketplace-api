from fastapi import APIRouter, status

from app.api.deps import CurrentClient, CurrentFreelancer, SessionDep
from app.schemas.bid import BidCreate, BidRead
from app.schemas.contract import ContractRead
from app.services.bid_service import accept_bid, create_bid, list_project_bids


router = APIRouter(tags=["Bids"])


@router.post(
    "/projects/{project_id}/bids",
    response_model=BidRead,
    status_code=status.HTTP_201_CREATED,
)
async def create_bid_endpoint(
    project_id: int,
    payload: BidCreate,
    db: SessionDep,
    current_freelancer: CurrentFreelancer,
):
    return create_bid(
        db,
        project_id=project_id,
        freelancer=current_freelancer,
        payload=payload,
    )


@router.get("/projects/{project_id}/bids", response_model=list[BidRead])
async def list_project_bids_endpoint(
    project_id: int,
    db: SessionDep,
    current_client: CurrentClient,
):
    return list_project_bids(db, project_id=project_id, client=current_client)


@router.post("/bids/{bid_id}/accept", response_model=ContractRead)
async def accept_bid_endpoint(
    bid_id: int,
    db: SessionDep,
    current_client: CurrentClient,
):
    return accept_bid(db, bid_id=bid_id, client=current_client)
