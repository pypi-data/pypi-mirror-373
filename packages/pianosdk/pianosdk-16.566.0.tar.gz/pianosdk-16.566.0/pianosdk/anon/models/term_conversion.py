from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.anon.models.access import Access
from pianosdk.anon.models.term import Term


class TermConversion(BaseModel):
    term_conversion_id: Optional[str] = None
    term: Optional['Term'] = None
    type: Optional[str] = None
    aid: Optional[str] = None
    user_access: Optional['Access'] = None
    create_date: Optional[datetime] = None


TermConversion.model_rebuild()
