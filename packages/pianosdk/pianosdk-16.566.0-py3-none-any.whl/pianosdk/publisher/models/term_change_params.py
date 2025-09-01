from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TermChangeParams(BaseModel):
    billing_timing: Optional[str] = None
    immediate_access: Optional[bool] = None
    prorate_access: Optional[bool] = None


TermChangeParams.model_rebuild()
