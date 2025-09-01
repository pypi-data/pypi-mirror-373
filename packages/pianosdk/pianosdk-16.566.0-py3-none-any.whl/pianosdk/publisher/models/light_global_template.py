from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.user import User


class LightGlobalTemplate(BaseModel):
    offer_template_id: Optional[str] = None
    aid: Optional[str] = None
    name: Optional[str] = None
    offer_template_name: Optional[str] = None
    description: Optional[str] = None
    create_date: Optional[datetime] = None
    create_by: Optional['User'] = None
    update_date: Optional[datetime] = None
    update_by: Optional['User'] = None
    publish_date: Optional[datetime] = None
    version: Optional[int] = None
    thumbnail_image_url: Optional[str] = None
    live_thumbnail_image_url: Optional[str] = None
    is_published: Optional[bool] = None
    count_variants: Optional[int] = None
    count_content_fields: Optional[int] = None
    deployment_id: Optional[str] = None
    status: Optional[str] = None


LightGlobalTemplate.model_rebuild()
