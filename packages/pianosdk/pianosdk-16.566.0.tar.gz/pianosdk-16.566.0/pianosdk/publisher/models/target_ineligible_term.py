from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TargetIneligibleTerm(BaseModel):
    term_id: Optional[str] = None
    name: Optional[str] = None
    tooltip: Optional[str] = None
    enabled: Optional[bool] = None


TargetIneligibleTerm.model_rebuild()
