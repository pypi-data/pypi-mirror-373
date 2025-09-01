from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TermFrom(BaseModel):
    name: Optional[str] = None
    type: Optional[str] = None
    from_term_id: Optional[str] = None
    from_term_name: Optional[str] = None
    from_period_id: Optional[str] = None
    from_period_name: Optional[str] = None


TermFrom.model_rebuild()
