from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class UpgradeOfferVariant(BaseModel):
    offer_id: Optional[str] = None
    name: Optional[str] = None


UpgradeOfferVariant.model_rebuild()
