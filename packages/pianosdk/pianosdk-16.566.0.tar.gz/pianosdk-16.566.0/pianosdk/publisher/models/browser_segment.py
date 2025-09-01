from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class BrowserSegment(BaseModel):
    segment_id: Optional[str] = None
    name: Optional[str] = None
    sort_order: Optional[int] = None
    filter: Optional[str] = None


BrowserSegment.model_rebuild()
