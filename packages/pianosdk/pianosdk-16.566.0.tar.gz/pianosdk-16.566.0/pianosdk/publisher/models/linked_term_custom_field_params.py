from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LinkedTermCustomFieldParams(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None


LinkedTermCustomFieldParams.model_rebuild()
