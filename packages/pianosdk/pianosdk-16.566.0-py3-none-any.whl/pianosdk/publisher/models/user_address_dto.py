from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UserAddressDto(BaseModel):
    company_name: Optional[str] = None
    country_name: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    region_name: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    phone: Optional[str] = None
    postal_code: Optional[str] = None
    city: Optional[str] = None


UserAddressDto.model_rebuild()
