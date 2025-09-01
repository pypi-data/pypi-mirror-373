from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.reallocation_batch import ReallocationBatch
from typing import List


class TermPeriodReallocation(BaseModel):
    term_pub_id: Optional[str] = None
    name: Optional[str] = None
    period_pub_id: Optional[str] = None
    next_period_sell_date: Optional[datetime] = None
    access_end_date: Optional[datetime] = None
    renewal_date: Optional[datetime] = None
    total_subscribers: Optional[int] = None
    subscribers_batches: Optional['List[ReallocationBatch]'] = None
    batches_with_pending_changes: Optional['List[ReallocationBatch]'] = None
    is_reallocation_in_progress: Optional[bool] = None


TermPeriodReallocation.model_rebuild()
