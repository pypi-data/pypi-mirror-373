from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class Resource(BaseModel):
    rid: Optional[str] = None
    aid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    image_url: Optional[str] = None


Resource.model_rebuild()
