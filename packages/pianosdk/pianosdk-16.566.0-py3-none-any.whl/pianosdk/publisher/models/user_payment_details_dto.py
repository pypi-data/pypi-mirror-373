from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.credit_guard_stored_fields import CreditGuardStoredFields
from pianosdk.publisher.models.term import Term
from pianosdk.publisher.models.user import User
from pianosdk.publisher.models.user_subscription import UserSubscription
from typing import Any


class UserPaymentDetailsDTO(BaseModel):
    user_payment_id: Optional[str] = None
    create_date: Optional[str] = None
    renewal: Optional[bool] = None
    refund_amount: Optional[float] = None
    remaining_amount: Optional[float] = None
    amount: Optional[float] = None
    price: Optional[str] = None
    refund_currency: Optional[str] = None
    currency: Optional[str] = None
    refundable: Optional[bool] = None
    subscription: Optional['UserSubscription'] = None
    term: Optional['Term'] = None
    user: Optional['User'] = None
    tax: Optional[float] = None
    hst_amount: Optional[float] = None
    qst_amount: Optional[float] = None
    pst_amount: Optional[float] = None
    gst_amount: Optional[float] = None
    tax_rate: Optional[float] = None
    hst_rate: Optional[float] = None
    qst_rate: Optional[float] = None
    pst_rate: Optional[float] = None
    gst_rate: Optional[float] = None
    tax_billing_country_code: Optional[str] = None
    tax_residence_country_code: Optional[str] = None
    zip_code: Optional[str] = None
    tax_billing_zip_code: Optional[str] = None
    geo_location_country: Optional[str] = None
    tax_billing_plan: Optional[str] = None
    billing_plan: Optional[str] = None
    user_payment_info_id: Optional[str] = None
    payment_method: Optional[str] = None
    transaction_details: Optional['Any'] = None
    source_id: Optional[int] = None
    source_name: Optional[str] = None
    upi_ext_customer_id: Optional[str] = None
    upi_ext_customer_id_label: Optional[str] = None
    external_transaction_id: Optional[str] = None
    tracking_id: Optional[str] = None
    original_price: Optional[str] = None
    status: Optional[str] = None
    status_value: Optional[int] = None
    refunded_amount: Optional[float] = None
    refund_amount_recalculated: Optional[bool] = None
    invoice_number: Optional[str] = None
    stored_fields: Optional['CreditGuardStoredFields'] = None


UserPaymentDetailsDTO.model_rebuild()
