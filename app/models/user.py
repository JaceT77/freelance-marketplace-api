from datetime import datetime

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import UserRole, values_enum
from app.models.timestamps import utcnow


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[UserRole] = mapped_column(values_enum(UserRole, name="user_role"))
    bio: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    projects: Mapped[list["Project"]] = relationship(
        back_populates="client",
        cascade="all, delete-orphan",
    )
    bids: Mapped[list["Bid"]] = relationship(
        back_populates="freelancer",
        cascade="all, delete-orphan",
    )
    client_contracts: Mapped[list["Contract"]] = relationship(
        back_populates="client",
        foreign_keys="Contract.client_id",
    )
    freelancer_contracts: Mapped[list["Contract"]] = relationship(
        back_populates="freelancer",
        foreign_keys="Contract.freelancer_id",
    )
