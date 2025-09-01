from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class AuditChangedFieldDto(BaseModel):
    field_name: Optional[str] = None
    new_value: Optional[str] = None
    old_value: Optional[str] = None
    diff: Optional[str] = None


AuditChangedFieldDto.model_rebuild()
