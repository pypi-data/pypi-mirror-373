from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.light_offer import LightOffer
from typing import List


class OfferList(BaseModel):
    purchase_offers: Optional['List[LightOffer]'] = None
    upgrade_offers: Optional['List[LightOffer]'] = None


OfferList.model_rebuild()
