from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.period_link_candidate import PeriodLinkCandidate
from typing import List


class LinkCandidate(BaseModel):
    term_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None
    payment_billing_plan_description: Optional[str] = None
    current_logic_id: Optional[str] = None
    current_logic_name: Optional[str] = None
    periods: Optional['List[PeriodLinkCandidate]'] = None


LinkCandidate.model_rebuild()
