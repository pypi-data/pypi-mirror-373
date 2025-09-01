from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class SectionsCounters(BaseModel):
    section: Optional[str] = None
    template_count: Optional[int] = None
    section_name_localized: Optional[str] = None


SectionsCounters.model_rebuild()
