from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import BidStatus
from app.schemas.user import UserSummary


class BidCreate(BaseModel):
    price: float = Field(gt=0)
    message: str = Field(min_length=5, max_length=2000)


class BidRead(BaseModel):
    id: int
    project_id: int
    price: float
    message: str
    created_at: datetime
    status: BidStatus
    freelancer: UserSummary

    model_config = ConfigDict(from_attributes=True)
