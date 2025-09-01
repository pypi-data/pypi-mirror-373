from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class GeoLocation(BaseModel):
    region_code: Optional[str] = None
    region_name: Optional[str] = None
    city: Optional[str] = None
    country_code: Optional[str] = None
    postal_code: Optional[str] = None


GeoLocation.model_rebuild()
