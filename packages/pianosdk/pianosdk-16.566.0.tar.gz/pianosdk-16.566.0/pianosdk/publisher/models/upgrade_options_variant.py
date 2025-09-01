from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class UpgradeOptionsVariant(BaseModel):
    term_id: Optional[str] = None
    term_name: Optional[str] = None
    period_id: Optional[str] = None
    period_name: Optional[str] = None
    payment_billing_plan: Optional[str] = None
    variant_type: Optional[str] = None
    prorate_disabled: Optional[str] = None
    immediate_access: Optional[str] = None
    available_billing_timings: Optional[List[int]] = None
    enabled: Optional[bool] = None
    tooltip: Optional[str] = None
    periods: Optional['List[UpgradeOptionsVariant]'] = None


UpgradeOptionsVariant.model_rebuild()
