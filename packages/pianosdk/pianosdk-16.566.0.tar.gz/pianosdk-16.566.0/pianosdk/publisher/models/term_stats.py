from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TermStats(BaseModel):
    pub_id: Optional[str] = None
    total_sale: Optional[str] = None
    total_sale_str: Optional[str] = None
    conversion: Optional[str] = None
    currency: Optional[str] = None


TermStats.model_rebuild()
