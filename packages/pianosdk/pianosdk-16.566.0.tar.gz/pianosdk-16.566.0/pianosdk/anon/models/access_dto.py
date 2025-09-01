from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.anon.models.resource_dto import ResourceDto
from pianosdk.anon.models.user_dto import UserDto


class AccessDTO(BaseModel):
    access_id: Optional[str] = None
    parent_access_id: Optional[str] = None
    granted: Optional[bool] = None
    user: Optional['UserDto'] = None
    resource: Optional['ResourceDto'] = None
    expire_date: Optional[datetime] = None
    start_date: Optional[datetime] = None
    can_revoke_access: Optional[bool] = None
    custom_data: Optional[str] = None


AccessDTO.model_rebuild()
