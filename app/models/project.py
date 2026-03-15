from datetime import date, datetime, timezone

from sqlalchemy import Date, DateTime, Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ProjectStatus


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(150), index=True)
    description: Mapped[str] = mapped_column(Text)
    budget: Mapped[float] = mapped_column(Float)
    deadline: Mapped[date] = mapped_column(Date)
    status: Mapped[ProjectStatus] = mapped_column(
        Enum(ProjectStatus, name="project_status"),
        default=ProjectStatus.OPEN,
        nullable=False,
    )
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=utcnow,
        nullable=False,
    )

    client: Mapped["User"] = relationship(back_populates="projects")
    bids: Mapped[list["Bid"]] = relationship(
        back_populates="project",
        cascade="all, delete-orphan",
    )
    contract: Mapped["Contract | None"] = relationship(
        back_populates="project",
        uselist=False,
    )
