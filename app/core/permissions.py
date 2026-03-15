from fastapi import HTTPException, status

from app.models.enums import UserRole


def require_role(user, role: UserRole):
    if user.role != role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Only {role.value}s can perform this action.",
        )
    return user


def require_project_owner(project, user) -> None:
    if project.client_id != user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not own this project.",
        )


def require_contract_party(contract, user) -> None:
    if user.id not in {contract.client_id, contract.freelancer_id}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this contract.",
        )
