from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class EraseSubscription(BaseModel):
    subscription_id: Optional[str] = None


EraseSubscription.model_rebuild()
