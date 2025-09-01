from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UserAliasDto(BaseModel):
    type: Optional[str] = None
    value: Optional[str] = None
    display_value: Optional[str] = None


UserAliasDto.model_rebuild()
