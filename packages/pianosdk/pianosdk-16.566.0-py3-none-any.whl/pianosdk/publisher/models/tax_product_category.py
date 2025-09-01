from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TaxProductCategory(BaseModel):
    caption: Optional[str] = None
    code: Optional[str] = None
    name: Optional[str] = None


TaxProductCategory.model_rebuild()
