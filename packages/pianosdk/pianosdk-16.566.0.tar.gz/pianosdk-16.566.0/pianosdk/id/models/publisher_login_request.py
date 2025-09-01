from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class PublisherLoginRequest(BaseModel):
    aid: Optional[str] = None
    email: Optional[str] = None
    password: Optional[str] = None
    stay_logged_in: Optional[bool] = None
    alias_name: Optional[str] = None
    login_type: Optional[str] = None


PublisherLoginRequest.model_rebuild()
