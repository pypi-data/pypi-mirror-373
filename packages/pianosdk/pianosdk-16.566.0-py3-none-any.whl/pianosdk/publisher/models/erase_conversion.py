from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class EraseConversion(BaseModel):
    term_conversion_id: Optional[str] = None
    browser: Optional[str] = None
    experience: Optional[str] = None
    user_address: Optional[str] = None
    geo_location: Optional[str] = None
    zone: Optional[str] = None


EraseConversion.model_rebuild()
