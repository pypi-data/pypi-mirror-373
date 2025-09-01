from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ShowOptionInChannelStats(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    count: Optional[int] = None


ShowOptionInChannelStats.model_rebuild()
