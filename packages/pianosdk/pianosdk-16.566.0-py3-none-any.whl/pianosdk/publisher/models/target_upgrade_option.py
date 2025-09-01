from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.billing_timing_option import BillingTimingOption
from typing import List


class TargetUpgradeOption(BaseModel):
    term_id: Optional[str] = None
    term_name: Optional[str] = None
    type: Optional[str] = None
    available_billing_timings: Optional['List[BillingTimingOption]'] = None
    description: Optional[str] = None
    billing_timing: Optional['BillingTimingOption'] = None
    immediate_access: Optional[bool] = None
    variant_type: Optional[str] = None
    period_id: Optional[str] = None
    period_name: Optional[str] = None
    enabled: Optional[bool] = None
    name: Optional[str] = None
    force_auto_renew: Optional[bool] = None


TargetUpgradeOption.model_rebuild()
