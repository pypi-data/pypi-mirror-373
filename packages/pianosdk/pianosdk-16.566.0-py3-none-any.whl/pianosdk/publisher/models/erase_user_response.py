from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.erase_contract_user import EraseContractUser
from pianosdk.publisher.models.erase_conversion import EraseConversion
from pianosdk.publisher.models.erase_subscription import EraseSubscription
from pianosdk.publisher.models.erase_transaction import EraseTransaction
from pianosdk.publisher.models.erase_user import EraseUser
from pianosdk.publisher.models.erase_user_address import EraseUserAddress
from pianosdk.publisher.models.erase_user_payment import EraseUserPayment
from pianosdk.publisher.models.erase_user_payment_info import EraseUserPaymentInfo
from pianosdk.publisher.models.erase_user_subscription_account import EraseUserSubscriptionAccount
from typing import List


class EraseUserResponse(BaseModel):
    user: Optional['EraseUser'] = None
    addresses: Optional['List[EraseUserAddress]'] = None
    subscriptions: Optional['List[EraseSubscription]'] = None
    upis: Optional['List[EraseUserPaymentInfo]'] = None
    payments: Optional['List[EraseUserPayment]'] = None
    transactions: Optional['List[EraseTransaction]'] = None
    conversions: Optional['List[EraseConversion]'] = None
    contract_users: Optional['List[EraseContractUser]'] = None
    shared_accounts: Optional['List[EraseUserSubscriptionAccount]'] = None


EraseUserResponse.model_rebuild()
