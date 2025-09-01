from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class GeoInfo(BaseModel):
    country: Optional[str] = None
    city: Optional[str] = None


GeoInfo.model_rebuild()
