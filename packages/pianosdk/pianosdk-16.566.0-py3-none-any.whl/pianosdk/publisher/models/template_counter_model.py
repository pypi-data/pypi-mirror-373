from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TemplateCounterModel(BaseModel):
    template_count: Optional[str] = None
    category: Optional[str] = None
    category_name_localized: Optional[str] = None


TemplateCounterModel.model_rebuild()
