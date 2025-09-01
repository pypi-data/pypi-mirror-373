from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class SourceEligibleTerm(BaseModel):
    variant_type: Optional[str] = None
    term_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    period_id: Optional[str] = None
    period_name: Optional[str] = None
    tooltip: Optional[str] = None
    enabled: Optional[bool] = None
    shared_account_limit: Optional[int] = None
    allow_collect_address: Optional[bool] = None


SourceEligibleTerm.model_rebuild()
