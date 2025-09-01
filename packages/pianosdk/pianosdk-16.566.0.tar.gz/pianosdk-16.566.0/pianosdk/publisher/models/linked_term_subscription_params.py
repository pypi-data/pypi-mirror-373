from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.linked_term_churn_params import LinkedTermChurnParams
from pianosdk.publisher.models.linked_term_purchase_params import LinkedTermPurchaseParams
from pianosdk.publisher.models.linked_term_upgrade_params import LinkedTermUpgradeParams
from typing import Dict
from typing import List


class LinkedTermSubscriptionParams(BaseModel):
    subscription_id: Optional[str] = None
    user_token: Optional[str] = None
    external_term_id: Optional[str] = None
    state: Optional[str] = None
    upgrade: Optional['LinkedTermUpgradeParams'] = None
    valid_to: Optional[int] = None
    auto_renew: Optional[bool] = None
    purchase: Optional['LinkedTermPurchaseParams'] = None
    churn: Optional['LinkedTermChurnParams'] = None
    access_custom_data: Optional[str] = None
    period: Optional[str] = None
    user_custom_fields: Optional[Dict[str, str]] = None


LinkedTermSubscriptionParams.model_rebuild()
