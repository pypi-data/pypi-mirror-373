from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.term_change_billing_options import TermChangeBillingOptions
from typing import List


class TermToEligible(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    enabled: Optional[str] = None
    tooltip: Optional[str] = None
    to_term_id: Optional[str] = None
    to_term_name: Optional[str] = None
    to_period_id: Optional[str] = None
    to_period_name: Optional[str] = None
    to_resource_id: Optional[str] = None
    to_resource_name: Optional[str] = None
    to_billing_plan: Optional[str] = None
    collect_address: Optional[bool] = None
    shared_account_count: Optional[int] = None
    available_billing_timings: Optional['List[TermChangeBillingOptions]'] = None
    prorate_restricted: Optional[bool] = None
    to_term_amount: Optional[float] = None
    authorisation_amount: Optional[float] = None
    to_term_amount_display: Optional[str] = None
    to_term_currency: Optional[str] = None
    prorate_amount: Optional[float] = None
    prorate_amount_display: Optional[str] = None
    prorate_refund_amount: Optional[float] = None


TermToEligible.model_rebuild()
