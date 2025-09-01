from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.term import Term


class SubscriptionLogItem(BaseModel):
    subscription_id: Optional[str] = None
    email: Optional[str] = None
    uid: Optional[str] = None
    rid: Optional[str] = None
    term: Optional['Term'] = None
    billing_plan: Optional[str] = None
    start_date: Optional[datetime] = None
    next_bill_date: Optional[datetime] = None
    status_name_in_reports: Optional[str] = None
    child_access: Optional[str] = None


SubscriptionLogItem.model_rebuild()
