from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LightOffer(BaseModel):
    offer_id: Optional[str] = None
    name: Optional[str] = None


LightOffer.model_rebuild()
