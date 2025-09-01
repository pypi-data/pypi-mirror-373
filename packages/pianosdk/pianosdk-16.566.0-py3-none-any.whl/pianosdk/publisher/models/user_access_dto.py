from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UserAccessDto(BaseModel):
    term_name: Optional[str] = None
    payment_billing_plan: Optional[str] = None
    billing_plan: Optional[str] = None
    image_url: Optional[str] = None
    resource_name: Optional[str] = None
    type: Optional[str] = None
    type_label: Optional[str] = None
    rid: Optional[str] = None
    term_id: Optional[str] = None
    create_date: Optional[str] = None
    expire_date: Optional[str] = None
    status: Optional[str] = None
    status_localized: Optional[str] = None
    access_id: Optional[str] = None


UserAccessDto.model_rebuild()
