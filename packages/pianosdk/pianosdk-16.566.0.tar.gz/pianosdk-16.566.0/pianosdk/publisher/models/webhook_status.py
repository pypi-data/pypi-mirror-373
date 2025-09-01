from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class WebhookStatus(BaseModel):
    status: Optional[str] = None
    description: Optional[str] = None


WebhookStatus.model_rebuild()
