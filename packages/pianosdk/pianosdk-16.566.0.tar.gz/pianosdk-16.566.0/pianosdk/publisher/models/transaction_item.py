from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TransactionItem(BaseModel):
    user_payment_id: Optional[str] = None
    name: Optional[str] = None
    payment_billing_plan: Optional[str] = None
    amount: Optional[float] = None
    refund_amount: Optional[float] = None
    payment_method: Optional[str] = None
    user_payment_info_id: Optional[str] = None
    payment_method_type: Optional[str] = None
    status: Optional[str] = None
    status_value: Optional[int] = None
    resource_image_url: Optional[str] = None
    resource_name: Optional[str] = None
    rid: Optional[str] = None
    currency_code: Optional[str] = None
    customer: Optional[str] = None
    _date: Optional[datetime] = None
    external_id: Optional[str] = None
    refund_external_tx_id: Optional[str] = None
    uid: Optional[str] = None
    term_id: Optional[str] = None
    price: Optional[float] = None
    price_display: Optional[str] = None
    currency: Optional[str] = None
    expires: Optional[int] = None
    taxed_price: Optional[str] = None
    upi_ext_customer_id: Optional[str] = None
    upi_ext_customer_id_label: Optional[str] = None
    transaction_type: Optional[str] = None
    currency_symbol: Optional[str] = None


TransactionItem.model_rebuild()
