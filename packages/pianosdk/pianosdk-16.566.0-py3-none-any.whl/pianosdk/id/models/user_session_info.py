from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.id.models.session import Session
from typing import List


class UserSessionInfo(BaseModel):
    sessions: Optional['List[Session]'] = None
    total: Optional[int] = None


UserSessionInfo.model_rebuild()
