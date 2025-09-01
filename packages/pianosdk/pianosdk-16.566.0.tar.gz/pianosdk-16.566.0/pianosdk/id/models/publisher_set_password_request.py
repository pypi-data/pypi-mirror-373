from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PublisherSetPasswordRequest(BaseModel):
    aid: Optional[str] = None
    reset_password_token: Optional[str] = None
    password: Optional[str] = None


PublisherSetPasswordRequest.model_rebuild()
