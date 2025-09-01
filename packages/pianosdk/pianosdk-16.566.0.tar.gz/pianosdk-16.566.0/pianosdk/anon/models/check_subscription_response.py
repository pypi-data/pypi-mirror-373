from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class CheckSubscriptionResponse(BaseModel):
    type: Optional[str] = None
    user_token: Optional[str] = None
    term_id: Optional[str] = None


CheckSubscriptionResponse.model_rebuild()
