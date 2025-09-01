from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class DynamicSubscriptionRenewalConfirmationDto(BaseModel):
    renewal_billing_plan: Optional[str] = None
    renewal_price: Optional[str] = None


DynamicSubscriptionRenewalConfirmationDto.model_rebuild()
