from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PaymentMethod(BaseModel):
    upi_nickname: Optional[str] = None
    upi_color: Optional[str] = None
    upi_number: Optional[str] = None
    upi_expiration_month: Optional[int] = None
    upi_expiration_year: Optional[int] = None
    upi_postal_code: Optional[str] = None
    description: Optional[str] = None
    user_payment_info_id: Optional[str] = None


PaymentMethod.model_rebuild()
