from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class SubscriptionUpgradeStatus(BaseModel):
    from_term_name: Optional[str] = None
    to_term_name: Optional[str] = None
    from_term_id: Optional[str] = None
    to_term_id: Optional[str] = None
    change_date: Optional[str] = None
    create_date_from: Optional[str] = None
    create_date_to: Optional[str] = None
    billing_plan_to: Optional[str] = None
    billing_plan_from: Optional[str] = None
    status: Optional[int] = None
    error_message: Optional[str] = None
    prorate_amount: Optional[str] = None
    prorate_refund_amount: Optional[str] = None


SubscriptionUpgradeStatus.model_rebuild()
