from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.models.enums import ProjectStatus
from app.schemas.user import UserSummary


class ProjectCreate(BaseModel):
    title: str = Field(min_length=3, max_length=150)
    description: str = Field(min_length=10)
    budget: float = Field(gt=0)
    deadline: date

    @field_validator("deadline")
    @classmethod
    def validate_deadline(cls, value: date) -> date:
        if value < date.today():
            raise ValueError("Deadline cannot be in the past.")
        return value


class ProjectRead(BaseModel):
    id: int
    title: str
    description: str
    budget: float
    deadline: date
    status: ProjectStatus
    created_at: datetime
    client: UserSummary

    model_config = ConfigDict(from_attributes=True)


class ProjectListResponse(BaseModel):
    items: list[ProjectRead]
    total: int
    page: int
    page_size: int
