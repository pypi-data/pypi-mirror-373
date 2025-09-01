from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UserModel(BaseModel):
    uid: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    valid: Optional[bool] = None


UserModel.model_rebuild()
