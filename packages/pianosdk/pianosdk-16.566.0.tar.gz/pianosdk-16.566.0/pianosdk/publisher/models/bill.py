from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Bill(BaseModel):
    bill_id: Optional[str] = None
    type: Optional[str] = None
    creation_date: Optional[str] = None
    status: Optional[str] = None
    url: Optional[str] = None
    rid: Optional[str] = None
    resource_name: Optional[str] = None
    resource_image_url: Optional[str] = None
    name: Optional[str] = None
    payment_billing_plan: Optional[str] = None
    cancelable: Optional[str] = None
    issued_to_email: Optional[str] = None


Bill.model_rebuild()
