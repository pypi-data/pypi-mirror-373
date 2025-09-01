from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ConsentModel(BaseModel):
    consent_pub_id: Optional[str] = None
    display_text: Optional[str] = None
    field_name: Optional[str] = None
    field_id: Optional[str] = None
    sort_order: Optional[int] = None
    checked: Optional[bool] = None
    required: Optional[bool] = None


ConsentModel.model_rebuild()
