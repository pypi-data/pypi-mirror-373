from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.user_address_dto import UserAddressDto


class TernChangeConfirmationDto(BaseModel):
    from_term_name: Optional[str] = None
    to_term_name: Optional[str] = None
    end_date: Optional[datetime] = None
    access_start_date: Optional[datetime] = None
    from_resource_name: Optional[str] = None
    to_resource_name: Optional[str] = None
    from_billing_plan: Optional[str] = None
    to_billing_plan: Optional[str] = None
    next_bill_date: Optional[datetime] = None
    prorate_refund_amount: Optional[str] = None
    prorate_amount: Optional[float] = None
    prorate_amount_display: Optional[str] = None
    prorate_amount_with_taxes: Optional[str] = None
    payment_method: Optional[str] = None
    user_address: Optional['UserAddressDto'] = None
    immediate_access: Optional[bool] = None
    immediate_billing: Optional[bool] = None
    to_term_amount: Optional[float] = None
    to_term_amount_display: Optional[str] = None
    to_term_amount_with_taxes: Optional[str] = None
    upi_expiration_month: Optional[int] = None
    upi_expiration_year: Optional[int] = None
    shared_account_limit: Optional[int] = None
    shared_account_count: Optional[int] = None
    prorate_access: Optional[bool] = None
    prorate_unused_amount: Optional[str] = None
    billing_timing_changed: Optional[bool] = None


TernChangeConfirmationDto.model_rebuild()
