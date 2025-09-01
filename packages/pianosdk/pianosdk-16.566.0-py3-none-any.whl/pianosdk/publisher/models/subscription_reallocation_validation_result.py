from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.subscription_reallocation_error import SubscriptionReallocationError
from typing import List


class SubscriptionReallocationValidationResult(BaseModel):
    subscription_reallocation_errors: Optional['List[SubscriptionReallocationError]'] = None


SubscriptionReallocationValidationResult.model_rebuild()
