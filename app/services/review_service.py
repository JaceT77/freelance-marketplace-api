from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.enums import ContractStatus
from app.models.review import Review
from app.models.user import User
from app.schemas.review import ReviewCreate
from app.services.contract_service import get_contract_by_id


def create_review(
    db: Session,
    *,
    contract_id: int,
    client: User,
    payload: ReviewCreate,
) -> Review:
    contract = get_contract_by_id(db, contract_id)
    if contract.client_id != client.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the client can leave a review for this contract.",
        )
    if contract.status != ContractStatus.FINISHED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reviews can only be created after the contract is finished.",
        )
    if contract.review is not None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A review already exists for this contract.",
        )

    review = Review(
        contract_id=contract.id,
        rating=payload.rating,
        comment=payload.comment,
    )
    db.add(review)
    db.commit()
    db.refresh(review)
    return review
