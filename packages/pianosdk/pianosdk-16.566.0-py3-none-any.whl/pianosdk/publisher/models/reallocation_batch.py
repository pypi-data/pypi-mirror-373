from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ReallocationBatch(BaseModel):
    subscribers_count: Optional[int] = None
    access_end_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None


ReallocationBatch.model_rebuild()
