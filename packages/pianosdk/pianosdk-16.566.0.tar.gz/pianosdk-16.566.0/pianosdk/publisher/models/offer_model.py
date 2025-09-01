from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.term import Term
from pianosdk.publisher.models.user import User
from typing import List


class OfferModel(BaseModel):
    aid: Optional[str] = None
    name: Optional[str] = None
    offer_id: Optional[str] = None
    status: Optional[str] = None
    deleted: Optional[bool] = None
    create_date: Optional[datetime] = None
    create_by: Optional['User'] = None
    update_date: Optional[datetime] = None
    update_by: Optional['User'] = None
    terms: Optional['List[Term]'] = None


OfferModel.model_rebuild()
