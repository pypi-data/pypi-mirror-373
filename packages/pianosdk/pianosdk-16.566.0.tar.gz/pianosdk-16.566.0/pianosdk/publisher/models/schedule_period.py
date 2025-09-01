from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class SchedulePeriod(BaseModel):
    period_id: Optional[str] = None
    name: Optional[str] = None
    sell_date: Optional[datetime] = None
    begin_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    status: Optional[str] = None


SchedulePeriod.model_rebuild()
