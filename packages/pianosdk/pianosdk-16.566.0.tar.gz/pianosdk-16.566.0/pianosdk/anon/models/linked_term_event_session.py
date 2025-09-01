from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.anon.models.linked_term_event_page_view_content import LinkedTermEventPageViewContent
from pianosdk.anon.models.linked_term_event_session_offer import LinkedTermEventSessionOffer


class LinkedTermEventSession(BaseModel):
    tracking_id: Optional[str] = None
    tbc: Optional[str] = None
    pcid: Optional[str] = None
    offer: Optional['LinkedTermEventSessionOffer'] = None
    page_view_id: Optional[str] = None
    page_view_content: Optional['LinkedTermEventPageViewContent'] = None
    user_agent: Optional[str] = None
    consents: Optional[str] = None
    previous_user_segments: Optional[str] = None
    user_state: Optional[str] = None


LinkedTermEventSession.model_rebuild()
