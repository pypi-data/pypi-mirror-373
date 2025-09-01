from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Notification(BaseModel):
    text: Optional[str] = None
    create_date: Optional[datetime] = None
    type: Optional[str] = None
    object_type: Optional[str] = None
    object_id: Optional[str] = None
    initiator: Optional[str] = None


Notification.model_rebuild()
