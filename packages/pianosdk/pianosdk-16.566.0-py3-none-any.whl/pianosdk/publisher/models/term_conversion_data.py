from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from typing import List


class TermConversionData(BaseModel):
    aid: Optional[str] = None
    offer_id: Optional[str] = None
    term_id: Optional[str] = None
    offer_template_id: Optional[str] = None
    template_id: Optional[str] = None
    uid: Optional[str] = None
    user_country: Optional[str] = None
    user_region: Optional[str] = None
    user_city: Optional[str] = None
    zip: Optional[str] = None
    latitude: Optional[str] = None
    longitude: Optional[str] = None
    user_agent: Optional[str] = None
    locale: Optional[str] = None
    hour: Optional[str] = None
    url: Optional[str] = None
    browser: Optional[str] = None
    platform: Optional[str] = None
    operating_system: Optional[str] = None
    tags: Optional[str] = None
    content_created: Optional[str] = None
    content_author: Optional[str] = None
    content_section: Optional[str] = None
    campaigns: Optional[List[str]] = None


TermConversionData.model_rebuild()
