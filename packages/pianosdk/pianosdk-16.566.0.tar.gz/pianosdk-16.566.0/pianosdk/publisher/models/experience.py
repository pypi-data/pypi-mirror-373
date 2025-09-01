from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Experience(BaseModel):
    experience_id: Optional[str] = None
    aid: Optional[str] = None
    type: Optional[str] = None
    cover_image_url: Optional[str] = None
    title: Optional[str] = None
    description: Optional[str] = None
    model: Optional[str] = None
    draft: Optional[str] = None
    draft_date: Optional[datetime] = None
    draft_base_version: Optional[int] = None
    create_date: Optional[datetime] = None
    create_by: Optional[str] = None
    update_date: Optional[datetime] = None
    update_by: Optional[str] = None
    version: Optional[int] = None
    schedule: Optional[str] = None
    status: Optional[str] = None
    hierarchy_type: Optional[str] = None
    parent_id: Optional[str] = None
    major_version: Optional[int] = None
    minor_version: Optional[int] = None


Experience.model_rebuild()
