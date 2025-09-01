from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PromotionFixedDiscount(BaseModel):
    fixed_discount_id: Optional[str] = None
    currency: Optional[str] = None
    amount: Optional[str] = None
    amount_value: Optional[float] = None


PromotionFixedDiscount.model_rebuild()
