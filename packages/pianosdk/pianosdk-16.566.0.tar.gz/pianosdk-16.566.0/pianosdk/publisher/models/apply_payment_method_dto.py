from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ApplyPaymentMethodDTO(BaseModel):
    updated_subscription_count: Optional[int] = None
    update_failed_subscription_count: Optional[int] = None


ApplyPaymentMethodDTO.model_rebuild()
