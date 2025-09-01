from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ConsentBoxEntry(BaseModel):
    field_name: Optional[str] = None
    display_text: Optional[str] = None
    entry: Optional[bool] = None
    create_date: Optional[datetime] = None
    type: Optional[str] = None


ConsentBoxEntry.model_rebuild()
