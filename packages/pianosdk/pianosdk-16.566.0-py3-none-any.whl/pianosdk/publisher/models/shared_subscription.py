from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.user_subscription_account import UserSubscriptionAccount
from typing import List


class SharedSubscription(BaseModel):
    subscription_id: Optional[str] = None
    term_id: Optional[str] = None
    uid: Optional[str] = None
    total_tokens: Optional[int] = None
    unused_tokens: Optional[int] = None
    redeemed_tokens: Optional[int] = None
    shared_accounts: Optional['List[UserSubscriptionAccount]'] = None


SharedSubscription.model_rebuild()
