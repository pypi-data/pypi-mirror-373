from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Tooltip(BaseModel):
    enabled: Optional[bool] = None
    type: Optional[str] = None
    text: Optional[str] = None


Tooltip.model_rebuild()
