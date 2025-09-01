from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class GracePeriodDetails(BaseModel):
    in_grace_period: Optional[bool] = None
    grace_period_start_date: Optional[datetime] = None
    grace_period_end_date: Optional[datetime] = None


GracePeriodDetails.model_rebuild()
