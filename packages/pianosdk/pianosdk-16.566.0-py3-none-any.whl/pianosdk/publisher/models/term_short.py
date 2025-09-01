from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TermShort(BaseModel):
    term_id: Optional[str] = None
    name: Optional[str] = None
    term_name: Optional[str] = None
    disabled: Optional[bool] = None
    tooltip: Optional[str] = None
    variant_type: Optional[str] = None
    period_id: Optional[str] = None
    period_name: Optional[str] = None


TermShort.model_rebuild()
