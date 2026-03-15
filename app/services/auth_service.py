from fastapi import HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.orm import Session

from app.core.hashing import hash_password, verify_password
from app.core.security import create_access_token
from app.models.user import User
from app.schemas.auth import RegisterRequest


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def register_user(db: Session, payload: RegisterRequest) -> User:
    existing_user = db.scalar(
        select(User).where(
            or_(User.username == payload.username, User.email == payload.email)
        )
    )
    if existing_user:
        detail = (
            "Username is already taken."
            if existing_user.username == payload.username
            else "Email is already registered."
        )
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
        role=payload.role,
        bio=payload.bio,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def authenticate_user(db: Session, username: str, password: str) -> User:
    user = db.scalar(select(User).where(User.username == username))
    if not user or not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials.",
        )
    return user


def build_token_response(user: User) -> dict:
    return {
        "access_token": create_access_token(str(user.id)),
        "token_type": "bearer",
        "user": user,
    }
