from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.user import User


class GlobalTemplateVersion(BaseModel):
    offer_template_id: Optional[str] = None
    token_type: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    aid: Optional[str] = None
    type: Optional[str] = None
    type_id: Optional[str] = None
    category_id: Optional[str] = None
    published: Optional[bool] = None
    publish_date: Optional[datetime] = None
    version: Optional[int] = None
    create_date: Optional[datetime] = None
    create_by: Optional['User'] = None
    update_date: Optional[datetime] = None
    update_by: Optional['User'] = None
    status: Optional[str] = None


GlobalTemplateVersion.model_rebuild()
