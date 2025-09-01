from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.access_period import AccessPeriod
from typing import List


class DynamicSubscriptionDetails(BaseModel):
    renewal_type: Optional[str] = None
    term_periods: Optional['List[AccessPeriod]'] = None
    scheduled_period_id: Optional[str] = None
    has_ongoing_periods: Optional[bool] = None
    can_renew_now: Optional[bool] = None
    can_be_resumed: Optional[bool] = None
    deferred_cancelable: Optional[bool] = None


DynamicSubscriptionDetails.model_rebuild()
