from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional


class EraseUserSubscriptionAccount(BaseModel):
    subscription_id: Optional[str] = None
    child_user_access_id: Optional[str] = None


EraseUserSubscriptionAccount.model_rebuild()
