from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TermLink(BaseModel):
    term_id: Optional[str] = None
    period_id: Optional[str] = None
    logic_id: Optional[str] = None
    name: Optional[str] = None
    default: Optional[bool] = None


TermLink.model_rebuild()
