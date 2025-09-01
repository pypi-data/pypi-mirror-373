from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LightExperience(BaseModel):
    experience_id: Optional[str] = None
    title: Optional[str] = None
    aid: Optional[str] = None
    app_name: Optional[str] = None


LightExperience.model_rebuild()
