from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.country import Country
from pianosdk.publisher.models.region import Region
from pianosdk.publisher.models.user import User


class UserAddressHistory(BaseModel):
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    revision: Optional[datetime] = None
    revision_type: Optional[int] = None
    user: Optional['User'] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company_name: Optional[str] = None
    address1: Optional[str] = None
    address2: Optional[str] = None
    city: Optional[str] = None
    postal_code: Optional[str] = None
    phone: Optional[str] = None
    user_address_id: Optional[str] = None
    deleted: Optional[bool] = None
    region: Optional['Region'] = None
    additional_fields: Optional[str] = None
    country: Optional['Country'] = None
    update_by: Optional[str] = None
    create_by: Optional[str] = None


UserAddressHistory.model_rebuild()
