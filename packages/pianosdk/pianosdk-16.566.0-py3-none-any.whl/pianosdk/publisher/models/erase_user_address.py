from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class EraseUserAddress(BaseModel):
    user_address_id: Optional[str] = None
    region_id: Optional[str] = None
    region_name: Optional[str] = None
    region_code: Optional[str] = None
    country_name: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    company_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    phone: Optional[str] = None
    additional_fields: Optional[str] = None


EraseUserAddress.model_rebuild()
