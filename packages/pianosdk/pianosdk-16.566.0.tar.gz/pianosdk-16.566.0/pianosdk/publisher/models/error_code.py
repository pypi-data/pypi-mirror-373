from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class ErrorCode(BaseModel):
    code: Optional[int] = None
    message: Optional[str] = None


ErrorCode.model_rebuild()
