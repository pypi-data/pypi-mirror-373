from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class CountrySimpleModel(BaseModel):
    country_code: Optional[str] = None
    pub_id: Optional[str] = None


CountrySimpleModel.model_rebuild()
