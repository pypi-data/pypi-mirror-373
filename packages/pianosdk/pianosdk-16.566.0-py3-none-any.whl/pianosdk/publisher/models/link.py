from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.period_link import PeriodLink
from typing import List


class Link(BaseModel):
    term_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    payment_billing_plan_description: Optional[str] = None
    rid: Optional[str] = None
    resource_name: Optional[str] = None
    periods: Optional['List[PeriodLink]'] = None


Link.model_rebuild()
