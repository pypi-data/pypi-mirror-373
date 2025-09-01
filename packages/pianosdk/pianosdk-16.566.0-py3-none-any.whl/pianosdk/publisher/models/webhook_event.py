from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.user import User
from pianosdk.publisher.models.webhook_response import WebhookResponse


class WebhookEvent(BaseModel):
    webhook_id: Optional[str] = None
    status: Optional[str] = None
    status_localized: Optional[str] = None
    retried: Optional[str] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    last_webhook_response: Optional['WebhookResponse'] = None
    user: Optional['User'] = None
    type: Optional[str] = None
    type_localized: Optional[str] = None
    event: Optional[str] = None
    event_localized: Optional[str] = None
    event_type: Optional[str] = None
    responses_count: Optional[int] = None


WebhookEvent.model_rebuild()
