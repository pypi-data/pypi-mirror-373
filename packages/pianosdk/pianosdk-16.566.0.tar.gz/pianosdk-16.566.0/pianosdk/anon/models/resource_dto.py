from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ResourceDto(BaseModel):
    rid: Optional[str] = None
    aid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


ResourceDto.model_rebuild()
