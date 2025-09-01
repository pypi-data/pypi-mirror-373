from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class WebhookConfig(BaseModel):
    key: Optional[str] = None
    label: Optional[str] = None
    enabled: Optional[bool] = None
    type: Optional[str] = None


WebhookConfig.model_rebuild()
