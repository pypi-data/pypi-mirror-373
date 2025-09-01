from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ExtendedExperienceRevision(BaseModel):
    model: Optional[str] = None
    draft: Optional[str] = None
    draft_date: Optional[datetime] = None
    draft_base_version: Optional[int] = None


ExtendedExperienceRevision.model_rebuild()
