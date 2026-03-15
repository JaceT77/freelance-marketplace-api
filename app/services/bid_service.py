from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.core.permissions import require_project_owner
from app.models.bid import Bid
from app.models.contract import Contract
from app.models.enums import BidStatus, ContractStatus, ProjectStatus
from app.models.project import Project
from app.models.user import User
from app.schemas.bid import BidCreate


def create_bid(
    db: Session,
    *,
    project_id: int,
    freelancer: User,
    payload: BidCreate,
) -> Bid:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )
    if project.status != ProjectStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Bids can only be placed on open projects.",
        )
    if project.client_id == freelancer.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot bid on your own project.",
        )

    existing_bid = db.scalar(
        select(Bid).where(
            Bid.project_id == project_id,
            Bid.freelancer_id == freelancer.id,
        )
    )
    if existing_bid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You have already placed a bid on this project.",
        )

    bid = Bid(
        project_id=project_id,
        freelancer_id=freelancer.id,
        price=payload.price,
        message=payload.message,
        status=BidStatus.PENDING,
    )
    db.add(bid)
    db.commit()
    db.refresh(bid)
    return get_bid_by_id(db, bid.id)


def get_bid_by_id(db: Session, bid_id: int) -> Bid:
    statement = (
        select(Bid)
        .options(selectinload(Bid.freelancer), selectinload(Bid.project))
        .where(Bid.id == bid_id)
    )
    bid = db.scalar(statement)
    if not bid:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Bid not found.",
        )
    return bid


def list_project_bids(db: Session, *, project_id: int, client: User) -> list[Bid]:
    project = db.get(Project, project_id)
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found.",
        )
    require_project_owner(project, client)

    statement = (
        select(Bid)
        .options(selectinload(Bid.freelancer))
        .where(Bid.project_id == project_id)
        .order_by(Bid.created_at.asc())
    )
    return list(db.scalars(statement).all())


def accept_bid(db: Session, *, bid_id: int, client: User) -> Contract:
    bid = get_bid_by_id(db, bid_id)
    project = bid.project
    require_project_owner(project, client)

    if project.status != ProjectStatus.OPEN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This project is no longer open for bid selection.",
        )
    if bid.status != BidStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only pending bids can be accepted.",
        )

    existing_contract = db.scalar(
        select(Contract).where(Contract.project_id == project.id)
    )
    if existing_contract:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A contract already exists for this project.",
        )

    project_bids = db.scalars(select(Bid).where(Bid.project_id == project.id)).all()
    for project_bid in project_bids:
        project_bid.status = (
            BidStatus.ACCEPTED if project_bid.id == bid.id else BidStatus.REJECTED
        )

    project.status = ProjectStatus.IN_PROGRESS
    contract = Contract(
        project_id=project.id,
        client_id=client.id,
        freelancer_id=bid.freelancer_id,
        agreed_price=bid.price,
        status=ContractStatus.ACTIVE,
    )
    db.add(contract)
    db.commit()

    return get_contract_by_id(db, contract.id)


def get_contract_by_id(db: Session, contract_id: int) -> Contract:
    statement = (
        select(Contract)
        .options(
            selectinload(Contract.client),
            selectinload(Contract.freelancer),
            selectinload(Contract.project),
        )
        .where(Contract.id == contract_id)
    )
    contract = db.scalar(statement)
    if not contract:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contract not found.",
        )
    return contract
