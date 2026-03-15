from datetime import datetime, timezone

from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session, selectinload

from app.core.permissions import require_contract_party
from app.models.contract import Contract
from app.models.enums import ContractStatus, ProjectStatus
from app.models.user import User


def get_contract_by_id(db: Session, contract_id: int) -> Contract:
    statement = (
        select(Contract)
        .options(
            selectinload(Contract.client),
            selectinload(Contract.freelancer),
            selectinload(Contract.project),
            selectinload(Contract.review),
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


def list_contracts_for_user(db: Session, user: User) -> list[Contract]:
    statement = (
        select(Contract)
        .options(selectinload(Contract.client), selectinload(Contract.freelancer))
        .where(or_(Contract.client_id == user.id, Contract.freelancer_id == user.id))
        .order_by(Contract.created_at.desc())
    )
    return list(db.scalars(statement).all())


def get_contract_for_user(db: Session, *, contract_id: int, user: User) -> Contract:
    contract = get_contract_by_id(db, contract_id)
    require_contract_party(contract, user)
    return contract


def finish_contract(db: Session, *, contract_id: int, client: User) -> Contract:
    contract = get_contract_by_id(db, contract_id)
    if contract.client_id != client.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the client can finish this contract.",
        )
    if contract.status != ContractStatus.ACTIVE:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only active contracts can be finished.",
        )

    contract.status = ContractStatus.FINISHED
    contract.finished_at = datetime.now(timezone.utc)
    contract.project.status = ProjectStatus.COMPLETED
    db.commit()
    return get_contract_by_id(db, contract.id)
