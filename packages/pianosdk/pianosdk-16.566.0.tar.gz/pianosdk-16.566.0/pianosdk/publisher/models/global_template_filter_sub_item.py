from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class GlobalTemplateFilterSubItem(BaseModel):
    id: Optional[str] = None
    name: Optional[str] = None
    counter_value: Optional[int] = None


GlobalTemplateFilterSubItem.model_rebuild()
