from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class SourceTermChangeVariant(BaseModel):
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
    available_billing_timings: Optional[List[int]] = None
    available_billing_timings_locked: Optional[bool] = None
    enabled: Optional[str] = None


SourceTermChangeVariant.model_rebuild()
