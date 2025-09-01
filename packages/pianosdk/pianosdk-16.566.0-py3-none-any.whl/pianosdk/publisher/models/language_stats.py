from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LanguageStats(BaseModel):
    template_keys_count: Optional[int] = None
    template_keys_abandoned: Optional[int] = None
    unit_keys_count: Optional[int] = None
    unit_keys_abandoned: Optional[int] = None
    locale: Optional[str] = None


LanguageStats.model_rebuild()
