from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LicenseeManager(BaseModel):
    uid: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    personal_name: Optional[str] = None


LicenseeManager.model_rebuild()
