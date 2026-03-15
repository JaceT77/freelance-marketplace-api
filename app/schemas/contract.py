from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ContractStatus
from app.schemas.user import UserSummary


class ContractRead(BaseModel):
    id: int
    project_id: int
    agreed_price: float
    status: ContractStatus
    created_at: datetime
    finished_at: datetime | None = None
    client: UserSummary
    freelancer: UserSummary

    model_config = ConfigDict(from_attributes=True)
