from datetime import date, datetime
from pydantic.main import BaseModel
from typing import Optional
from pianosdk.publisher.models.app import App
from pianosdk.publisher.models.braintree_merchant_account_id_entry import BraintreeMerchantAccountIdEntry
from pianosdk.publisher.models.payee_settings_entry import PayeeSettingsEntry
from typing import List


class BraintreeConfiguration(BaseModel):
    configuration_id: Optional[str] = None
    app: Optional['App'] = None
    source_name: Optional[str] = None
    title: Optional[str] = None
    braintree_merchant_id: Optional[str] = None
    braintree_client_key: Optional[str] = None
    braintree_merchant_accounts: Optional['List[BraintreeMerchantAccountIdEntry]'] = None
    braintree_public_key: Optional[str] = None
    braintree_private_key: Optional[str] = None
    is_disabled: Optional[bool] = None
    is_editable: Optional[bool] = None
    is_paypal_enabled: Optional[bool] = None
    is_apple_pay_enabled: Optional[bool] = None
    braintree_descriptor: Optional[str] = None
    braintree_trial_descriptor: Optional[str] = None
    braintree_app_name_custom_field: Optional[str] = None
    payee_settings: Optional['List[PayeeSettingsEntry]'] = None
    is_visible: Optional[bool] = None
    version: Optional[str] = None
    version_title: Optional[str] = None
    use_moto: Optional[bool] = None
    default_currency: Optional[str] = None
    collect_cardholder_name: Optional[bool] = None
    fraud_protection_enabled: Optional[bool] = None


BraintreeConfiguration.model_rebuild()
