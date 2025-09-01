from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.country_simple_model import CountrySimpleModel
from pianosdk.publisher.models.region_simple_model import RegionSimpleModel


class UserBillingAddress(BaseModel):
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    address_line3: Optional[str] = None
    country: Optional['CountrySimpleModel'] = None
    region: Optional['RegionSimpleModel'] = None
    region_name: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    type: Optional[str] = None
    verified: Optional[str] = None
    address_pub_id: Optional[str] = None


UserBillingAddress.model_rebuild()
