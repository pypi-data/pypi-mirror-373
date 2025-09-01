from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PublisherPasswordRequest(BaseModel):
    aid: Optional[str] = None
    uid: Optional[str] = None
    password: Optional[str] = None
    current_password: Optional[str] = None
    force_update: Optional[bool] = None


PublisherPasswordRequest.model_rebuild()
