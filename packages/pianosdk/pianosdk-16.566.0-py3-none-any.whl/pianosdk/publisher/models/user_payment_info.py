from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UserPaymentInfo(BaseModel):
    user_payment_info_id: Optional[str] = None
    description: Optional[str] = None
    upi_nickname: Optional[str] = None
    upi_number: Optional[str] = None
    upi_expiration_month: Optional[int] = None
    upi_expiration_year: Optional[int] = None
    upi_postal_code: Optional[str] = None
    upi_identifier: Optional[str] = None
    payment_method: Optional[str] = None
    payment_type: Optional[str] = None
    issuer_country_code: Optional[str] = None
    is_mock: Optional[bool] = None


UserPaymentInfo.model_rebuild()
