from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class CustomFieldValueDto(BaseModel):
    field_name: Optional[str] = None
    value: Optional[str] = None
    created: Optional[datetime] = None
    email_creator: Optional[str] = None
    sort_order: Optional[int] = None


CustomFieldValueDto.model_rebuild()
