from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.resource import Resource
from pianosdk.publisher.models.user import User


class Access(BaseModel):
    access_id: Optional[str] = None
    parent_access_id: Optional[str] = None
    granted: Optional[bool] = None
    revoked: Optional[bool] = None
    resource: Optional['Resource'] = None
    user: Optional['User'] = None
    expire_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    can_revoke_access: Optional[bool] = None


Access.model_rebuild()
