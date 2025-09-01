from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class LinkedTermPageViewContentParams(BaseModel):
    content_created: Optional[str] = None
    content_author: Optional[str] = None
    content_section: Optional[str] = None
    content_type: Optional[str] = None
    tags: Optional[List[str]] = None


LinkedTermPageViewContentParams.model_rebuild()
