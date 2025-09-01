from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.linked_term_conversion_params import LinkedTermConversionParams
from pianosdk.publisher.models.linked_term_shared_access_params import LinkedTermSharedAccessParams
from pianosdk.publisher.models.linked_term_subscription_params import LinkedTermSubscriptionParams


class LinkedTermEventRequest(BaseModel):
    action: Optional[str] = None
    session_id: Optional[str] = None
    subscription: Optional['LinkedTermSubscriptionParams'] = None
    conversion: Optional['LinkedTermConversionParams'] = None
    shared_access: Optional['LinkedTermSharedAccessParams'] = None


LinkedTermEventRequest.model_rebuild()
