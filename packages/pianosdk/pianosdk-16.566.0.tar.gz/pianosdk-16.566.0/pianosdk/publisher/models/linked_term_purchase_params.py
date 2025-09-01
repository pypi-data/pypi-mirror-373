from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LinkedTermPurchaseParams(BaseModel):
    trial: Optional[str] = None


LinkedTermPurchaseParams.model_rebuild()
