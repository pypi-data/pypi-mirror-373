from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.country_model import CountryModel


class AvalaraOriginAddress(BaseModel):
    address_line1: Optional[str] = None
    country: Optional['CountryModel'] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    state: Optional[str] = None
    reference_field: Optional[str] = None


AvalaraOriginAddress.model_rebuild()
