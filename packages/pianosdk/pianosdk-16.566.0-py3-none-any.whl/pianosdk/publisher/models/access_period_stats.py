from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class AccessPeriodStats(BaseModel):
    access_period_id: Optional[str] = None
    active_subscription_count: Optional[int] = None
    scheduled_subscription_count: Optional[int] = None


AccessPeriodStats.model_rebuild()
