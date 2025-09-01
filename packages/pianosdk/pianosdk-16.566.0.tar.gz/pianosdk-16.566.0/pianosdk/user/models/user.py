from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class User(BaseModel):
    uid: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    personal_name: Optional[str] = None
    email: Optional[str] = None
    image1: Optional[str] = None


User.model_rebuild()
