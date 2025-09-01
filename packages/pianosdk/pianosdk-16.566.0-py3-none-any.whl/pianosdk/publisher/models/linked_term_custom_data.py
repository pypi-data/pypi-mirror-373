from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LinkedTermCustomData(BaseModel):
    value: Optional[str] = None


LinkedTermCustomData.model_rebuild()
