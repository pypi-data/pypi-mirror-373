from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Period(BaseModel):
    name: Optional[str] = None
    period_id: Optional[str] = None
    sell_date: Optional[datetime] = None
    begin_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    deleted: Optional[bool] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    is_sale_started: Optional[bool] = None
    is_active: Optional[bool] = None


Period.model_rebuild()
