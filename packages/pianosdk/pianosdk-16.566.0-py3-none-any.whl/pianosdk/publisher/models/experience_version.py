from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ExperienceVersion(BaseModel):
    experience_id: Optional[str] = None
    version: Optional[int] = None
    minor_version: Optional[int] = None
    major_version: Optional[int] = None
    committed: Optional[bool] = None
    committed_date: Optional[datetime] = None
    revision_notes: Optional[str] = None


ExperienceVersion.model_rebuild()
