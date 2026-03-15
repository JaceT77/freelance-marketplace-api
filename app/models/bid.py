from datetime import datetime, timezone

from sqlalchemy import (
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import BidStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Bid(Base):
    __tablename__ = "bids"
    __table_args__ = (
        UniqueConstraint("project_id", "freelancer_id", name="uq_bid_project_freelancer"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id", ondelete="CASCADE"))
    freelancer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    price: Mapped[float] = mapped_column(Float)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )
    status: Mapped[BidStatus] = mapped_column(
        Enum(BidStatus, name="bid_status"),
        default=BidStatus.PENDING,
        nullable=False,
    )

    project: Mapped["Project"] = relationship(back_populates="bids")
    freelancer: Mapped["User"] = relationship(back_populates="bids")
