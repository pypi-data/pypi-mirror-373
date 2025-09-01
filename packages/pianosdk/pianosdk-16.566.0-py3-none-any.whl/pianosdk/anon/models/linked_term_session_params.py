from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.anon.models.linked_term_page_view_content_params import LinkedTermPageViewContentParams


class LinkedTermSessionParams(BaseModel):
    tracking_id: Optional[str] = None
    tbc: Optional[str] = None
    pcid: Optional[str] = None
    offer_id: Optional[str] = None
    offer_template_id: Optional[str] = None
    offer_template_version_id: Optional[str] = None
    page_view_id: Optional[str] = None
    page_view_content: Optional['LinkedTermPageViewContentParams'] = None
    consents: Optional[str] = None
    previous_user_segments: Optional[str] = None
    user_state: Optional[str] = None


LinkedTermSessionParams.model_rebuild()
