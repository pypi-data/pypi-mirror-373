from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TaxCountry(BaseModel):
    country_name: Optional[str] = None
    country_code: Optional[str] = None
    requires_zip_code: Optional[bool] = None
    need_residence: Optional[bool] = None
    include_billing: Optional[bool] = None
    tax_support: Optional[str] = None


TaxCountry.model_rebuild()
