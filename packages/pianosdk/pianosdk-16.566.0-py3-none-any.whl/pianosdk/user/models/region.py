from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Region(BaseModel):
    region_name: Optional[str] = None
    region_code: Optional[str] = None
    region_id: Optional[str] = None


Region.model_rebuild()
