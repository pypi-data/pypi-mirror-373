from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class EraseUser(BaseModel):
    uid: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


EraseUser.model_rebuild()
