from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class SourceIneligibleTerm(BaseModel):
    variant_type: Optional[str] = None
    term_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    from_period_id: Optional[str] = None
    from_period_name: Optional[str] = None
    tooltip: Optional[str] = None
    enabled: Optional[bool] = None


SourceIneligibleTerm.model_rebuild()
