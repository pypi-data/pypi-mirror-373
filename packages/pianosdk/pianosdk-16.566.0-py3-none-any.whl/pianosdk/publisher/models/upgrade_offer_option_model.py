from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UpgradeOfferOptionModel(BaseModel):
    term_change_option_id: Optional[str] = None
    description: Optional[str] = None
    from_term_id: Optional[str] = None
    from_term_name: Optional[str] = None
    from_period_id: Optional[str] = None
    from_period_name: Optional[str] = None
    from_billing_plan: Optional[str] = None
    to_term_id: Optional[str] = None
    to_term_name: Optional[str] = None
    to_period_id: Optional[str] = None
    to_period_name: Optional[str] = None
    to_billing_plan: Optional[str] = None
    billing_timing: Optional[str] = None
    immediate_access: Optional[str] = None
    prorate_access: Optional[str] = None


UpgradeOfferOptionModel.model_rebuild()
