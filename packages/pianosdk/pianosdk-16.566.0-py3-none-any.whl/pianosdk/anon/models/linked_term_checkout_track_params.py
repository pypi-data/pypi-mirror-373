from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LinkedTermCheckoutTrackParams(BaseModel):
    aid: Optional[str] = None
    browser_id: Optional[str] = None
    external_term_id: Optional[str] = None
    checkout_start_date: Optional[int] = None


LinkedTermCheckoutTrackParams.model_rebuild()
