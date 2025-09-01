from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.linked_term_payment_params import LinkedTermPaymentParams


class LinkedTermConversionParams(BaseModel):
    conversion_id: Optional[str] = None
    create_date: Optional[int] = None
    payment: Optional['LinkedTermPaymentParams'] = None


LinkedTermConversionParams.model_rebuild()
