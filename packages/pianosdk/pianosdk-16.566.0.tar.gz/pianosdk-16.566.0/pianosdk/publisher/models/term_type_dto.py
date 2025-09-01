from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TermTypeDTO(BaseModel):
    type_id: Optional[str] = None
    type_name: Optional[str] = None
    type_enum_name: Optional[str] = None


TermTypeDTO.model_rebuild()
