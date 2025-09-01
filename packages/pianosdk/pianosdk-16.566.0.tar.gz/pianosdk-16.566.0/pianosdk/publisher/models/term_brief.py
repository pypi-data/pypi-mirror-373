from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TermBrief(BaseModel):
    term_id: Optional[str] = None
    name: Optional[str] = None
    disabled: Optional[bool] = None


TermBrief.model_rebuild()
