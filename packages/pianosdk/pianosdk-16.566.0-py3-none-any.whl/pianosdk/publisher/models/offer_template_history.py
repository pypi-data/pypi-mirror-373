from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.offer_template_sub_history import OfferTemplateSubHistory
from typing import List


class OfferTemplateHistory(BaseModel):
    history_content: Optional[str] = None
    history_comment: Optional[str] = None
    offer_template_history_event: Optional[str] = None
    offer_template_id: Optional[str] = None
    history_list: Optional['List[OfferTemplateSubHistory]'] = None


OfferTemplateHistory.model_rebuild()
