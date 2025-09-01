from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.anon.models.external_css import ExternalCss
from typing import List


class LightOfferTemplateVersion(BaseModel):
    offer_template_id: Optional[str] = None
    token_type: Optional[str] = None
    version: Optional[int] = None
    type: Optional[str] = None
    content1_type: Optional[str] = None
    content2_type: Optional[str] = None
    content3_type: Optional[str] = None
    content1_value: Optional[str] = None
    content2_value: Optional[str] = None
    content3_value: Optional[str] = None
    template_id: Optional[str] = None
    template_version_id: Optional[str] = None
    is_offer_template_archived: Optional[bool] = None
    is_template_variant_archived: Optional[bool] = None
    external_css_list: Optional['List[ExternalCss]'] = None


LightOfferTemplateVersion.model_rebuild()
