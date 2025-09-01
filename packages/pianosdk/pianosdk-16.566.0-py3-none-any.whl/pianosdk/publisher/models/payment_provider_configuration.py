from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.app import App
from pianosdk.publisher.models.braintree_merchant_account_id_entry import BraintreeMerchantAccountIdEntry
from pianosdk.publisher.models.currency import Currency
from typing import List


class PaymentProviderConfiguration(BaseModel):
    configuration_id: Optional[str] = None
    app: Optional['App'] = None
    source_name: Optional[str] = None
    title: Optional[str] = None
    braintree_merchant_id: Optional[str] = None
    braintree_client_key: Optional[str] = None
    braintree_merchant_accounts: Optional['List[BraintreeMerchantAccountIdEntry]'] = None
    mock_currencies: Optional['List[Currency]'] = None
    is_disabled: Optional[bool] = None
    is_editable: Optional[bool] = None
    braintree_descriptor: Optional[str] = None
    braintree_trial_descriptor: Optional[str] = None
    is_visible: Optional[bool] = None


PaymentProviderConfiguration.model_rebuild()
