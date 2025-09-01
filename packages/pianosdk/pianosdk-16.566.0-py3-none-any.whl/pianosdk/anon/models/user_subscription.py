from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.anon.models.term import Term


class UserSubscription(BaseModel):
    subscription_id: Optional[str] = None
    term: Optional['Term'] = None
    auto_renew: Optional[bool] = None
    grace_period_start_date: Optional[datetime] = None
    next_bill_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    create_date: Optional[datetime] = None
    status: Optional[str] = None
    cancelable: Optional[bool] = None
    cancelable_and_refundadle: Optional[bool] = None
    payment_billing_plan_description: Optional[str] = None
    external_sub_id: Optional[str] = None
    access_custom_data: Optional[str] = None


UserSubscription.model_rebuild()
