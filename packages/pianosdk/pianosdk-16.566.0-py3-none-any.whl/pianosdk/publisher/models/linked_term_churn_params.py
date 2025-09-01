from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LinkedTermChurnParams(BaseModel):
    type: Optional[str] = None
    amount: Optional[float] = None
    currency: Optional[str] = None


LinkedTermChurnParams.model_rebuild()
