from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.term_period_reallocation import TermPeriodReallocation
from typing import List


class TermReallocation(BaseModel):
    name: Optional[str] = None
    term_type: Optional[str] = None
    term_pub_id: Optional[str] = None
    periods: Optional['List[TermPeriodReallocation]'] = None
    active_period_count: Optional[int] = None
    active_subscribers_count: Optional[int] = None


TermReallocation.model_rebuild()
