from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.currency import Currency


class Money(BaseModel):
    amount: Optional[float] = None
    currency: Optional['Currency'] = None


Money.model_rebuild()
