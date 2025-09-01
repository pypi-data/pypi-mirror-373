from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class CountryModel(BaseModel):
    country_name: Optional[str] = None
    country_code: Optional[str] = None


CountryModel.model_rebuild()
