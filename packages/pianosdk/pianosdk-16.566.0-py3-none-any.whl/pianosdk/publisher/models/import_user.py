from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ImportUser(BaseModel):
    email: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None


ImportUser.model_rebuild()
