from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ExperienceMetadata(BaseModel):
    aid: Optional[str] = None
    experience_id: Optional[str] = None
    title: Optional[str] = None
    type: Optional[str] = None
    status: Optional[str] = None
    hierarchy_type: Optional[str] = None
    parent_id: Optional[str] = None
    create_date: Optional[datetime] = None
    create_by: Optional[str] = None
    update_date: Optional[datetime] = None
    update_by: Optional[str] = None
    description: Optional[str] = None
    schedule: Optional[str] = None
    deleted: Optional[bool] = None
    major_version: Optional[int] = None
    minor_version: Optional[int] = None


ExperienceMetadata.model_rebuild()
