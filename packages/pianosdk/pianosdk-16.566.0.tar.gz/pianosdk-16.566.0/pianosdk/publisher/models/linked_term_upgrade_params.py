from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class LinkedTermUpgradeParams(BaseModel):
    from_subscription_id: Optional[str] = None


LinkedTermUpgradeParams.model_rebuild()
