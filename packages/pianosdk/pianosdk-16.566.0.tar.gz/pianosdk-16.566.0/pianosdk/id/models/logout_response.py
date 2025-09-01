from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LogoutResponse(BaseModel):
    jti: Optional[str] = None


LogoutResponse.model_rebuild()
