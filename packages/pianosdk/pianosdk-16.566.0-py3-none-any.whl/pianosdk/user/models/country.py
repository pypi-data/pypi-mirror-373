from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Country(BaseModel):
    country_name: Optional[str] = None
    country_code: Optional[str] = None
    country_id: Optional[str] = None


Country.model_rebuild()
