from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class AccessPeriod(BaseModel):
    period_id: Optional[str] = None
    name: Optional[str] = None
    billing_description: Optional[str] = None
    type: Optional[str] = None
    enabled: Optional[bool] = None
    removed: Optional[bool] = None
    tooltip: Optional[str] = None


AccessPeriod.model_rebuild()
