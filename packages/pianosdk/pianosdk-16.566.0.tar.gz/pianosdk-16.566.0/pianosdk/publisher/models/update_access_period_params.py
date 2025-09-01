from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.duration import Duration


class UpdateAccessPeriodParams(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    access_end_date: Optional[date] = None
    total_iterations: Optional[int] = None
    duration: Optional['Duration'] = None
    amount: Optional[float] = None
    billing_type: Optional[str] = None
    billing_duration: Optional['Duration'] = None
    billing_day: Optional[int] = None
    billing_month: Optional[int] = None
    subscription_cancellation_allowed: Optional[bool] = None


UpdateAccessPeriodParams.model_rebuild()
