from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class AppResourceCount(BaseModel):
    aid: Optional[str] = None
    resource_count: Optional[int] = None


AppResourceCount.model_rebuild()
