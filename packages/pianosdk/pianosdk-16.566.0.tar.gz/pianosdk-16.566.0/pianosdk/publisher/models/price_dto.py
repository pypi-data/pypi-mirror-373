from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PriceDTO(BaseModel):
    currency_code: Optional[str] = None
    amount: Optional[float] = None
    currency_symbol: Optional[str] = None
    display: Optional[str] = None


PriceDTO.model_rebuild()
