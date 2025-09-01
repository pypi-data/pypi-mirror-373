from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TranslationMapRevision(BaseModel):
    version: Optional[int] = None
    create_date: Optional[datetime] = None
    update_date: Optional[datetime] = None
    published: Optional[bool] = None
    editing: Optional[bool] = None
    draft: Optional[bool] = None


TranslationMapRevision.model_rebuild()
