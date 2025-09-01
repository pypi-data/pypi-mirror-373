from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LicenseeRepresentative(BaseModel):
    email: Optional[str] = None


LicenseeRepresentative.model_rebuild()
