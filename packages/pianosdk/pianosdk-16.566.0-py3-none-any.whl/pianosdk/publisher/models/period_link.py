from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PeriodLink(BaseModel):
    access_period_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    payment_billing_plan_description: Optional[str] = None
    removed: Optional[bool] = None


PeriodLink.model_rebuild()
