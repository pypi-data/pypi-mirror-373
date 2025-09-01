from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.user_billing_address import UserBillingAddress
from typing import Any
from typing import Dict
from typing import List


class PaymentMethodDTO(BaseModel):
    user_payment_info_id: Optional[str] = None
    description: Optional[str] = None
    upi_identifier: Optional[str] = None
    upi_nickname: Optional[str] = None
    upi_cardholder: Optional[str] = None
    upi_first_name: Optional[str] = None
    upi_last_name: Optional[str] = None
    upi_number: Optional[str] = None
    state: Optional[str] = None
    upi_expiration_month: Optional[int] = None
    upi_expiration_year: Optional[int] = None
    upi_postal_code: Optional[str] = None
    upi_email: Optional[str] = None
    upi_card_country_code: Optional[str] = None
    upi_card_zip_code: Optional[str] = None
    upi_country_state: Optional[str] = None
    upi_city: Optional[str] = None
    upi_street: Optional[str] = None
    currency: Optional[str] = None
    next_bill_date: Optional[str] = None
    readonly: Optional[bool] = None
    can_be_edited: Optional[bool] = None
    can_be_deleted: Optional[bool] = None
    can_be_set_default: Optional[bool] = None
    source_id: Optional[str] = None
    source_name: Optional[str] = None
    upi_ext_customer_id: Optional[str] = None
    upi_ext_customer_id_label: Optional[str] = None
    upi_ext_payment_id: Optional[str] = None
    tax_residence_country_code: Optional[str] = None
    tax_billing_country_code: Optional[str] = None
    tax_billing_zip_code: Optional[str] = None
    user_billing_address: Optional['UserBillingAddress'] = None
    stored_fields: Optional[str] = None
    payment_instrument_data: Optional['Dict[str, Any]'] = None


PaymentMethodDTO.model_rebuild()
