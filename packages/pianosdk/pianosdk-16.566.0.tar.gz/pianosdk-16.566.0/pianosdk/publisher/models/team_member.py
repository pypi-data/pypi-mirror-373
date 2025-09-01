from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class TeamMember(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    personal_name: Optional[str] = None
    email: Optional[str] = None
    uid: Optional[str] = None
    create_date: Optional[datetime] = None
    last_login: Optional[datetime] = None
    invitation_expired: Optional[bool] = None
    permissions: Optional[List[str]] = None


TeamMember.model_rebuild()
