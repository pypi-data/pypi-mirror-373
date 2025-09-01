from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class TargetTermChangeVariant(BaseModel):
    name: Optional[str] = None
    term_id: Optional[str] = None
    term_name: Optional[str] = None
    term_type: Optional[str] = None
    period_id: Optional[str] = None
    period_name: Optional[str] = None
    payment_billing_plan: Optional[str] = None
    variant_type: Optional[str] = None
    tooltip: Optional[str] = None
    prorate_disabled: Optional[str] = None
    enabled: Optional[str] = None
    available_billing_timings: Optional[List[int]] = None


TargetTermChangeVariant.model_rebuild()
