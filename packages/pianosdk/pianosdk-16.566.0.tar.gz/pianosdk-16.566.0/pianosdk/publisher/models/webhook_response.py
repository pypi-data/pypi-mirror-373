from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class WebhookResponse(BaseModel):
    status: Optional[str] = None
    status_localized: Optional[str] = None
    response_headers: Optional[str] = None
    response_body: Optional[str] = None
    create_date: Optional[datetime] = None
    request_url: Optional[str] = None
    request_data: Optional[str] = None


WebhookResponse.model_rebuild()
