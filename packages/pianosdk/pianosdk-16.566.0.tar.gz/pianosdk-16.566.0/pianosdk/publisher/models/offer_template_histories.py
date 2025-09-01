from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.offer_template_history import OfferTemplateHistory
from typing import List


class OfferTemplateHistories(BaseModel):
    history_list: Optional['List[OfferTemplateHistory]'] = None


OfferTemplateHistories.model_rebuild()
