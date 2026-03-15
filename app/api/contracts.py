from fastapi import APIRouter

from app.api.deps import CurrentClient, CurrentUser, SessionDep
from app.schemas.contract import ContractRead
from app.services.contract_service import (
    finish_contract,
    get_contract_for_user,
    list_contracts_for_user,
)


router = APIRouter(prefix="/contracts", tags=["Contracts"])


@router.get("", response_model=list[ContractRead])
async def list_contracts_endpoint(db: SessionDep, current_user: CurrentUser):
    return await list_contracts_for_user(db, current_user)


@router.get("/{contract_id}", response_model=ContractRead)
async def get_contract_endpoint(
    contract_id: int,
    db: SessionDep,
    current_user: CurrentUser,
):
    return await get_contract_for_user(db, contract_id=contract_id, user=current_user)


@router.post("/{contract_id}/finish", response_model=ContractRead)
async def finish_contract_endpoint(
    contract_id: int,
    db: SessionDep,
    current_client: CurrentClient,
):
    return await finish_contract(db, contract_id=contract_id, client=current_client)
