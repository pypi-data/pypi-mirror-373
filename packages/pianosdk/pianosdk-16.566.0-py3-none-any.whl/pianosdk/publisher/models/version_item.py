from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class VersionItem(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    aid: Optional[str] = None
    type: Optional[str] = None
    published: Optional[bool] = None
    version: Optional[int] = None
    update_date: Optional[datetime] = None


VersionItem.model_rebuild()
