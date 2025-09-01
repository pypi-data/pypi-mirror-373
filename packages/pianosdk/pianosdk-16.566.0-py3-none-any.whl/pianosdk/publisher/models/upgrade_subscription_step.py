from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.billing_timing_option import BillingTimingOption
from pianosdk.publisher.models.term_short import TermShort


class UpgradeSubscriptionStep(BaseModel):
    from_term: Optional['TermShort'] = None
    to_term: Optional['TermShort'] = None
    billing_timing: Optional['BillingTimingOption'] = None
    immediate_access: Optional[bool] = None
    include_auto_renew_off: Optional[bool] = None
    do_not_send_emails: Optional[bool] = None
    do_not_send_cancellation_emails: Optional[bool] = None


UpgradeSubscriptionStep.model_rebuild()
