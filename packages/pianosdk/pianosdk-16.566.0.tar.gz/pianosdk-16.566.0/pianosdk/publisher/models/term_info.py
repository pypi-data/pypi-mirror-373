from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TermInfo(BaseModel):
    id: Optional[str] = None
    title: Optional[str] = None
    billing: Optional[str] = None


TermInfo.model_rebuild()
