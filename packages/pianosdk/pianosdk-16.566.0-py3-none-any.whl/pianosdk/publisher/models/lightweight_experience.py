from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LightweightExperience(BaseModel):
    experience_id: Optional[str] = None
    title: Optional[str] = None


LightweightExperience.model_rebuild()
