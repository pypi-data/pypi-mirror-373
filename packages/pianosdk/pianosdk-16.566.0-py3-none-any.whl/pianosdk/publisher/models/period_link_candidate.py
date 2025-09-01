from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PeriodLinkCandidate(BaseModel):
    access_period_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    payment_billing_plan_description: Optional[str] = None
    current_logic_id: Optional[str] = None
    current_logic_name: Optional[str] = None
    removed: Optional[bool] = None


PeriodLinkCandidate.model_rebuild()
