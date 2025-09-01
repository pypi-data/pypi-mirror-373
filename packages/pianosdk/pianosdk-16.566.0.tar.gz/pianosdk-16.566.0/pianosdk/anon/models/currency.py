from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Currency(BaseModel):
    currency_code: Optional[str] = None
    currency_symbol: Optional[str] = None


Currency.model_rebuild()
