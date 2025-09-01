from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class C2ExperienceConfig(BaseModel):
    aid: Optional[str] = None
    version: Optional[int] = None
    js: Optional[str] = None
    published: Optional[bool] = None
    published_date: Optional[datetime] = None


C2ExperienceConfig.model_rebuild()
