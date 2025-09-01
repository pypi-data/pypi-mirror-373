from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.user.models.country import Country
from pianosdk.user.models.region import Region


class UserAddress(BaseModel):
    user_address_id: Optional[str] = None
    region: Optional['Region'] = None
    country: Optional['Country'] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    personal_name: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    phone: Optional[str] = None


UserAddress.model_rebuild()
