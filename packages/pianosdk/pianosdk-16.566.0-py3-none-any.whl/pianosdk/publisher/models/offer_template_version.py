from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.external_css import ExternalCss
from pianosdk.publisher.models.offer_template_content_field import OfferTemplateContentField
from pianosdk.publisher.models.offer_template_variant import OfferTemplateVariant
from pianosdk.publisher.models.user import User
from typing import List


class OfferTemplateVersion(BaseModel):
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
    content1_type: Optional[str] = None
    content2_type: Optional[str] = None
    content3_type: Optional[str] = None
    content1_value: Optional[str] = None
    content2_value: Optional[str] = None
    content3_value: Optional[str] = None
    version: Optional[int] = None
    publish_date: Optional[datetime] = None
    type: Optional[str] = None
    type_id: Optional[str] = None
    boilerplate_type: Optional[str] = None
    boilerplate_type_id: Optional[str] = None
    category_id: Optional[str] = None
    thumbnail_image_url: Optional[str] = None
    live_thumbnail_image_url: Optional[str] = None
    published: Optional[bool] = None
    external_css_list: Optional['List[ExternalCss]'] = None
    has_preview: Optional[bool] = None
    status: Optional[str] = None
    variant_list: Optional['List[OfferTemplateVariant]'] = None
    content_field_list: Optional['List[OfferTemplateContentField]'] = None
    is_global: Optional[bool] = None
    is_inherited: Optional[bool] = None


OfferTemplateVersion.model_rebuild()
