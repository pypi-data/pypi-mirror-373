from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.period import Period
from typing import List


class Schedule(BaseModel):
    aid: Optional[str] = None
    name: Optional[str] = None
    schedule_id: Optional[str] = None
    deleted: Optional[bool] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    periods: Optional['List[Period]'] = None


Schedule.model_rebuild()
