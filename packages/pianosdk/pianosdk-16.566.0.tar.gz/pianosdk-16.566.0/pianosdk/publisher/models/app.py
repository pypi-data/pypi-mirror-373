from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class App(BaseModel):
    aid: Optional[str] = None
    default_lang: Optional[str] = None
    email_lang: Optional[str] = None
    details: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    user_provider: Optional[str] = None
    url: Optional[str] = None
    logo1: Optional[str] = None
    logo2: Optional[str] = None
    state: Optional[str] = None
    private_key: Optional[str] = None
    api_token: Optional[str] = None


App.model_rebuild()
