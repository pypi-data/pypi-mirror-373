from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class EraseUserPaymentInfo(BaseModel):
    user_payment_info_id: Optional[str] = None
    billing_zip_code: Optional[str] = None
    residence_country: Optional[str] = None
    provider_fields: Optional[str] = None
    upi_nickname: Optional[str] = None
    upi_postal_code: Optional[str] = None
    funding_source: Optional[str] = None
    pin_code: Optional[str] = None
    account_number: Optional[str] = None
    external_transaction_id: Optional[str] = None
    upi_ext_customer_id: Optional[str] = None


EraseUserPaymentInfo.model_rebuild()
