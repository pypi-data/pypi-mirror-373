from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.offer_template_content_field import OfferTemplateContentField
from pianosdk.publisher.models.offer_template_variant import OfferTemplateVariant
from pianosdk.publisher.models.user import User
from typing import List


class OfferTemplate(BaseModel):
    offer_template_id: Optional[str] = None
    token_type: Optional[str] = None
    aid: Optional[str] = None
    app_name: Optional[str] = None
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
    boilerplate_type: Optional[str] = None
    boilerplate_type_id: Optional[str] = None
    category_id: Optional[str] = None
    thumbnail_image_url: Optional[str] = None
    live_thumbnail_image_url: Optional[str] = None
    status: Optional[str] = None
    is_published: Optional[bool] = None
    count_variants: Optional[int] = None
    variant_list: Optional['List[OfferTemplateVariant]'] = None
    archived_date: Optional[datetime] = None
    archived_by: Optional['User'] = None
    content_field_list: Optional['List[OfferTemplateContentField]'] = None
    can_be_global: Optional[bool] = None
    is_global: Optional[bool] = None
    is_inherited: Optional[bool] = None


OfferTemplate.model_rebuild()
