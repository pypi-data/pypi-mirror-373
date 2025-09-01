from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.user.models.resource import Resource
from pianosdk.user.models.user import User


class Access(BaseModel):
    access_id: Optional[str] = None
    parent_access_id: Optional[str] = None
    granted: Optional[bool] = None
    user: Optional['User'] = None
    resource: Optional['Resource'] = None
    expire_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    can_revoke_access: Optional[bool] = None


Access.model_rebuild()
