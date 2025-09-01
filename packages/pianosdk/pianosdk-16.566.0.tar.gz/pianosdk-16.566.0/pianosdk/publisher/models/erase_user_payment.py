from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class EraseUserPayment(BaseModel):
    user_payment_id: Optional[str] = None
    tax: Optional[str] = None
    billing_region: Optional[str] = None
    residence_region: Optional[str] = None
    ui_caption: Optional[str] = None
    name: Optional[str] = None
    address: Optional[str] = None
    geo_location_country: Optional[str] = None
    geo_location: Optional[str] = None


EraseUserPayment.model_rebuild()
