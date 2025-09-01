from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.term import Term
from pianosdk.publisher.models.term_conversion_subscription import TermConversionSubscription


class UserPaymentDTO(BaseModel):
    user_payment_id: Optional[str] = None
    create_date: Optional[str] = None
    user_payment_state: Optional[str] = None
    renewal: Optional[bool] = None
    amount: Optional[float] = None
    price: Optional[str] = None
    currency: Optional[str] = None
    refundable: Optional[bool] = None
    subscription: Optional['TermConversionSubscription'] = None
    term: Optional['Term'] = None
    tax: Optional[float] = None
    tax_billing_plan: Optional[str] = None
    payment_method: Optional[str] = None
    upi_ext_customer_id: Optional[str] = None
    upi_ext_customer_id_label: Optional[str] = None
    external_transaction_id: Optional[str] = None
    tracking_id: Optional[str] = None
    original_price: Optional[str] = None


UserPaymentDTO.model_rebuild()
