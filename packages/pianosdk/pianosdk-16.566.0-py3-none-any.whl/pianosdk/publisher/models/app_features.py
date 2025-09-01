from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.composer import Composer
from pianosdk.publisher.models.my_account import MyAccount
from pianosdk.publisher.models.redemption_page import RedemptionPage
from pianosdk.publisher.models.subscription_restrictions import SubscriptionRestrictions


class AppFeatures(BaseModel):
    my_account: Optional['MyAccount'] = None
    composer: Optional['Composer'] = None
    subscription_restrictions: Optional['SubscriptionRestrictions'] = None
    redemption_page: Optional['RedemptionPage'] = None
    is_payment_mock_enabled: Optional[bool] = None
    is_publisher_dashboard_localization_enabled: Optional[bool] = None
    is_checkout_authentication_in_separate_state: Optional[bool] = None


AppFeatures.model_rebuild()
