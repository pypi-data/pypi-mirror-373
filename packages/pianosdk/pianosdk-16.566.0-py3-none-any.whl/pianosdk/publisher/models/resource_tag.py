from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ResourceTag(BaseModel):
    resource_tag_id: Optional[str] = None
    name: Optional[str] = None
    type: Optional[str] = None


ResourceTag.model_rebuild()
