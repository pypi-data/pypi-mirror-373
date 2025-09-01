from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class TemplateUserModel(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[str] = None
    uid: Optional[str] = None


TemplateUserModel.model_rebuild()
