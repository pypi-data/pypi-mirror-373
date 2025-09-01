from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class BillingPlanTranslationRequest(BaseModel):
    billing_plan: Optional[str] = None
    subscription_last_payment: Optional[datetime] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    term_pub_id: Optional[str] = None


BillingPlanTranslationRequest.model_rebuild()
