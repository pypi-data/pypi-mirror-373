from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UserAudit(BaseModel):
    uid: Optional[str] = None
    action_type: Optional[str] = None
    aid: Optional[str] = None


UserAudit.model_rebuild()
