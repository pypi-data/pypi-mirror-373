from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LinkedTermPaymentParams(BaseModel):
    amount: Optional[float] = None
    currency: Optional[str] = None


LinkedTermPaymentParams.model_rebuild()
