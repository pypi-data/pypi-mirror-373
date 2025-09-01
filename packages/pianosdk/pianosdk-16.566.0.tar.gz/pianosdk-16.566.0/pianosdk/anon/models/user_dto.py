from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UserDto(BaseModel):
    uid: Optional[str] = None
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    personal_name: Optional[str] = None
    create_date: Optional[datetime] = None


UserDto.model_rebuild()
