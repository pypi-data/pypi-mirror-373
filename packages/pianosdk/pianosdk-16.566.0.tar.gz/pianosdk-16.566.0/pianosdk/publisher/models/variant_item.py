from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class VariantItem(BaseModel):
    name: Optional[str] = None
    update_date: Optional[int] = None


VariantItem.model_rebuild()
