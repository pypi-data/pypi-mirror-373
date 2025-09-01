from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ExternalAPIField(BaseModel):
    field_name: Optional[str] = None
    field_title: Optional[str] = None
    description: Optional[str] = None
    mandatory: Optional[bool] = None
    hidden: Optional[bool] = None
    default_value: Optional[str] = None
    order: Optional[int] = None
    type: Optional[str] = None
    editable: Optional[str] = None


ExternalAPIField.model_rebuild()
