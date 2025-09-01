from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ConsentModel(BaseModel):
    consent_pub_id: Optional[str] = None
    display_text: Optional[str] = None
    field_name: Optional[str] = None
    field_id: Optional[str] = None
    sort_order: Optional[str] = None
    checked: Optional[str] = None


ConsentModel.model_rebuild()
