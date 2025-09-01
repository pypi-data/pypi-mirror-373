from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Duration(BaseModel):
    value: Optional[int] = None
    unit: Optional[str] = None


Duration.model_rebuild()
