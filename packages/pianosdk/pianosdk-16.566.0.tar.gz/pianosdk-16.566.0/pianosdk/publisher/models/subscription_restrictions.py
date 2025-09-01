from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class SubscriptionRestrictions(BaseModel):
    allow_change_next_bill_date: Optional[bool] = None
    allow_enable_auto_renew: Optional[bool] = None
    allow_switch_payment_method: Optional[bool] = None
    allow_scheduler_renewals: Optional[bool] = None
    allow_future_renewals: Optional[bool] = None
    allow_verify_now: Optional[bool] = None
    allow_activate_now: Optional[bool] = None


SubscriptionRestrictions.model_rebuild()
