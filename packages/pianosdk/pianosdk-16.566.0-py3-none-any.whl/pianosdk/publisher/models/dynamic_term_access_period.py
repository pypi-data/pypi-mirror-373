from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class DynamicTermAccessPeriod(BaseModel):
    term_id: Optional[str] = None
    period_id: Optional[str] = None
    removed: Optional[bool] = None
    access_end_date: Optional[datetime] = None


DynamicTermAccessPeriod.model_rebuild()
