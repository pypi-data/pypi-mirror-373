from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TermToIneligible(BaseModel):
    type: Optional[str] = None
    to_term_id: Optional[str] = None
    to_term_name: Optional[str] = None
    to_resource_id: Optional[str] = None
    to_resource_name: Optional[str] = None
    collect_address: Optional[bool] = None
    shared_account_count: Optional[int] = None
    tooltip: Optional[str] = None


TermToIneligible.model_rebuild()
