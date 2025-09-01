from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.offer_template_content_field import OfferTemplateContentField
from pianosdk.publisher.models.template_user_model import TemplateUserModel
from typing import List


class OfferTemplateVariant(BaseModel):
    offer_template_variant_id: Optional[str] = None
    offer_template_id: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    live_thumbnail_image_url: Optional[str] = None
    deleted: Optional[bool] = None
    create_date: Optional[datetime] = None
    create_by: Optional['TemplateUserModel'] = None
    update_date: Optional[datetime] = None
    update_by: Optional['TemplateUserModel'] = None
    archived_date: Optional[datetime] = None
    archived_by: Optional['TemplateUserModel'] = None
    status: Optional[str] = None
    content_field_list: Optional['List[OfferTemplateContentField]'] = None
    is_inherited: Optional[bool] = None


OfferTemplateVariant.model_rebuild()
