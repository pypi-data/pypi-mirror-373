from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UserRef(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    uid: Optional[str] = None
    create_date: Optional[datetime] = None


UserRef.model_rebuild()
