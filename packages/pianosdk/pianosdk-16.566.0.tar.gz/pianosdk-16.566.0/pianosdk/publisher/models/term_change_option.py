from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.advanced_options import AdvancedOptions
from pianosdk.publisher.models.light_offer import LightOffer
from typing import List


class TermChangeOption(BaseModel):
    term_change_option_id: Optional[str] = None
    from_term_id: Optional[str] = None
    from_term_name: Optional[str] = None
    from_period_id: Optional[str] = None
    from_period_name: Optional[str] = None
    from_resource_id: Optional[str] = None
    from_resource_name: Optional[str] = None
    from_billing_plan: Optional[str] = None
    to_term_id: Optional[str] = None
    to_term_name: Optional[str] = None
    to_period_id: Optional[str] = None
    to_period_name: Optional[str] = None
    to_resource_id: Optional[str] = None
    to_resource_name: Optional[str] = None
    to_billing_plan: Optional[str] = None
    billing_timing: Optional[str] = None
    immediate_access: Optional[bool] = None
    prorate_access: Optional[bool] = None
    description: Optional[str] = None
    include_trial: Optional[bool] = None
    to_scheduled: Optional[bool] = None
    from_scheduled: Optional[bool] = None
    shared_account_count: Optional[int] = None
    collect_address: Optional[bool] = None
    upgrade_offers: Optional['List[LightOffer]'] = None
    advanced_options: Optional['AdvancedOptions'] = None


TermChangeOption.model_rebuild()
