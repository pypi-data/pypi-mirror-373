from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class EarlyBillingDetails(BaseModel):
    enabled: Optional[bool] = None
    in_progress: Optional[bool] = None
    billing_date: Optional[datetime] = None


EarlyBillingDetails.model_rebuild()
