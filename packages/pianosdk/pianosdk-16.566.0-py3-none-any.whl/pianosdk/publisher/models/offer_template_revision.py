from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.user import User


class OfferTemplateRevision(BaseModel):
    offer_template_id: Optional[str] = None
    token_type: Optional[str] = None
    aid: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    deleted: Optional[bool] = None
    create_date: Optional[datetime] = None
    create_by: Optional['User'] = None
    update_date: Optional[datetime] = None
    update_by: Optional['User'] = None
    publish_date: Optional[datetime] = None
    version: Optional[int] = None
    type: Optional[str] = None
    type_id: Optional[str] = None
    is_published: Optional[bool] = None
    content_loaded: Optional[bool] = None
    content1_type: Optional[str] = None
    content2_type: Optional[str] = None
    content1_value: Optional[str] = None
    content2_value: Optional[str] = None


OfferTemplateRevision.model_rebuild()
