from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UserDto(BaseModel):
    uid: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    personal_name: Optional[str] = None
    email: Optional[str] = None
    image1: Optional[str] = None


UserDto.model_rebuild()
