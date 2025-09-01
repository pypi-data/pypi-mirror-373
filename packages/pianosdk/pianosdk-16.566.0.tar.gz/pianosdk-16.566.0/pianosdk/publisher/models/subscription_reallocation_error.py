from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class SubscriptionReallocationError(BaseModel):
    error_message: Optional[str] = None
    error_element_index: Optional[int] = None
    field_name: Optional[str] = None


SubscriptionReallocationError.model_rebuild()
