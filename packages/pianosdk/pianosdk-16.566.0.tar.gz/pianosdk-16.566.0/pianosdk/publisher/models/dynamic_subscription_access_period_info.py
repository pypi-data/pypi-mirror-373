from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class DynamicSubscriptionAccessPeriodInfo(BaseModel):
    access_period_id: Optional[str] = None
    name: Optional[str] = None
    total_iterations: Optional[int] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    iteration: Optional[int] = None
    payment_billing_plan: Optional[str] = None
    length: Optional[str] = None
    is_imported_access_period: Optional[bool] = None
    status: Optional[str] = None
    next_bill_date: Optional[datetime] = None


DynamicSubscriptionAccessPeriodInfo.model_rebuild()
