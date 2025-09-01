from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ContractDetails(BaseModel):
    contract_id: Optional[str] = None
    name: Optional[str] = None
    contract_type: Optional[str] = None
    contract_is_active: Optional[bool] = None
    contract_has_schedule: Optional[bool] = None
    seats_number: Optional[int] = None
    is_hard_seats_limit_type: Optional[bool] = None
    contract_allocated_users_count: Optional[int] = None
    contract_redeemed_users_count: Optional[int] = None
    create_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


ContractDetails.model_rebuild()
