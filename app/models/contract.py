from datetime import datetime

from sqlalchemy import DateTime, Float, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ContractStatus, values_enum
from app.models.timestamps import utcnow


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    project_id: Mapped[int] = mapped_column(
        ForeignKey("projects.id", ondelete="CASCADE"),
        unique=True,
    )
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    freelancer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    agreed_price: Mapped[float] = mapped_column(Float)
    status: Mapped[ContractStatus] = mapped_column(
        values_enum(ContractStatus, name="contract_status"),
        default=ContractStatus.ACTIVE,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )
    finished_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    project: Mapped["Project"] = relationship(back_populates="contract")
    client: Mapped["User"] = relationship(
        back_populates="client_contracts",
        foreign_keys=[client_id],
    )
    freelancer: Mapped["User"] = relationship(
        back_populates="freelancer_contracts",
        foreign_keys=[freelancer_id],
    )
    review: Mapped["Review | None"] = relationship(
        back_populates="contract",
        uselist=False,
        cascade="all, delete-orphan",
    )
