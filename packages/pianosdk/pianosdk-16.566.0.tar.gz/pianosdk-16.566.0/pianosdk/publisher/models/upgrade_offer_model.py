from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.upgrade_offer_option_model import UpgradeOfferOptionModel
from typing import List


class UpgradeOfferModel(BaseModel):
    aid: Optional[str] = None
    offer_id: Optional[str] = None
    name: Optional[str] = None
    upgrade_offer_options: Optional['List[UpgradeOfferOptionModel]'] = None


UpgradeOfferModel.model_rebuild()
